import json
from pathlib import Path

import numpy as np
from django.core.management.base import BaseCommand
from django.db.models import Avg
from django.utils import timezone

from main.models import Enrollment, Grade, Attendance


class Command(BaseCommand):
    help = "Обучает простую ML‑модель прогноза итоговой оценки и сохраняет артефакты."

    def add_arguments(self, parser):
        parser.add_argument(
            "--save-path",
            type=str,
            default="models/grade_model.pkl",
            help="Путь для сохранения модели",
        )

    def handle(self, *args, **options):
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.preprocessing import StandardScaler
            from sklearn.model_selection import train_test_split
            import joblib
        except Exception as exc:  # pragma: no cover - зависимость может отсутствовать
            self.stderr.write(self.style.ERROR(f"scikit-learn/joblib не установлены: {exc}"))
            return

        save_path = Path(options["save_path"])
        save_path.parent.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.MIGRATE_HEADING("=== Обучение модели прогноза оценок ==="))

        X, y, feature_names = self._build_dataset()
        if len(X) < 20:
            self.stderr.write(
                self.style.WARNING("Недостаточно данных для обучения модели (нужно >= 20 записей).")
            )
            return

        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model = LinearRegression()
        model.fit(X_train_scaled, y_train)

        preds = model.predict(X_test_scaled)
        rmse = float(np.sqrt(np.mean((preds - y_test) ** 2)))
        r2 = float(1 - np.sum((y_test - preds) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2))

        joblib.dump(
            {
                "model": model,
                "scaler": scaler,
                "feature_names": feature_names,
                "trained_at": timezone.now().isoformat(),
            },
            save_path,
        )

        metrics_path = save_path.parent / "metrics.json"
        metrics = {
            "rmse": rmse,
            "r2": r2,
            "n_samples": int(len(X)),
            "n_features": len(feature_names),
            "feature_names": feature_names,
        }
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

        self.stdout.write(
            self.style.SUCCESS(
                f"Модель сохранена в {save_path}, метрики в {metrics_path} (RMSE={rmse:.2f}, R2={r2:.3f})"
            )
        )

    def _build_dataset(self):
        """
        Формирует выборку на основе Enrollment/Attendance/Grade.
        Целевая переменная: итоговая оценка (финальный экзамен).
        """
        X = []
        y = []
        feature_names = [
            "attendance_rate",
            "avg_homework",
            "midterm_score",
            "previous_gpa",
        ]

        enrollments = Enrollment.objects.all().select_related("student", "course")
        for enr in enrollments:
            grades_qs = Grade.objects.filter(enrollment=enr)
            if not grades_qs.exists():
                continue

            final_grade = grades_qs.filter(assignment_name__icontains="Финальный").order_by(
                "-date"
            ).first()
            if not final_grade:
                # fallback: максимальная оценка как итоговая
                final_grade = grades_qs.order_by("-value").first()
            if not final_grade:
                continue

            # Признак: посещаемость
            att_qs = Attendance.objects.filter(enrollment=enr)
            attendance_rate = 1.0
            if att_qs.exists():
                total = att_qs.count()
                present = att_qs.filter(present=True).count()
                attendance_rate = present / total if total else 1.0

            # Признак: средний балл за домашние задания
            hw_avg = grades_qs.filter(assignment_name__icontains="Домашнее").aggregate(
                avg=Avg("value")
            )["avg"]
            if hw_avg is None:
                hw_avg = grades_qs.exclude(assignment_name__icontains="Финал").aggregate(
                    avg=Avg("value")
                )["avg"] or 0

            # Признак: midterm
            midterm = grades_qs.filter(assignment_name__icontains="Midterm").order_by(
                "-date"
            ).first()
            midterm_score = float(midterm.value) if midterm else float(hw_avg)

            # Признак: предыдущий GPA (средняя оценка по другим курсам)
            previous_grades = Grade.objects.filter(
                student=enr.student.user if enr.student.user else None
            ).exclude(course=enr.course)
            if previous_grades.exists():
                previous_gpa = float(previous_grades.aggregate(avg=Avg("value"))["avg"] or 0)
            else:
                previous_gpa = float(hw_avg)

            X.append(
                [
                    float(attendance_rate * 100.0),
                    float(hw_avg),
                    float(midterm_score),
                    float(previous_gpa),
                ]
            )
            y.append(float(final_grade.value))

        return X, y, feature_names



