from pathlib import Path
import json

from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse

from .models import Student, Group, Course, Lecture


class SeedDemoTests(TestCase):
    def test_seed_demo_creates_data(self):
        call_command("seed_demo", students=10, groups=3, courses=5, seed=1)
        self.assertGreater(Student.objects.count(), 0)
        self.assertGreater(Group.objects.count(), 0)
        self.assertGreater(Course.objects.count(), 0)
        self.assertGreater(Lecture.objects.count(), 0)

        # Идемпотентность: повторный запуск не должен падать
        call_command("seed_demo", students=10, groups=3, courses=5, seed=1)


class TrainModelTests(TestCase):
    def setUp(self):
        call_command("seed_demo", students=30, groups=5, courses=5, seed=2)

    def test_train_grade_model_outputs_files(self):
        models_dir = Path("models")
        model_path = models_dir / "grade_model.pkl"
        metrics_path = models_dir / "metrics.json"

        call_command("train_grade_model", save_path=str(model_path))

        self.assertTrue(model_path.exists())
        self.assertTrue(metrics_path.exists())

        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        self.assertIn("rmse", metrics)
        self.assertIn("r2", metrics)


class ApiTests(TestCase):
    def setUp(self):
        call_command("seed_demo", students=20, groups=3, courses=3, seed=3)
        # Обучаем модель для предсказания
        models_dir = Path("models")
        model_path = models_dir / "grade_model.pkl"
        call_command("train_grade_model", save_path=str(model_path))
        # Индексируем лекции (может упасть в BM25 fallback, это нормально)
        call_command("index_lectures")

        from django.contrib.auth.models import User

        self.staff = User.objects.create_user(
            username="admin", password="admin123", is_staff=True
        )

    def test_predict_grade_api(self):
        from .models import Enrollment

        enrollment = Enrollment.objects.first()
        client = Client()
        client.login(username="admin", password="admin123")

        url = reverse("api_predict_grade")
        resp = client.post(
            url,
            data=json.dumps(
                {
                    "student_id": enrollment.student_id,
                    "course_id": enrollment.course_id,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("predicted_final_grade", data)

    def test_search_resources_api(self):
        client = Client()
        url = reverse("api_search_resources")
        resp = client.post(
            url,
            data=json.dumps({"q": "программирование", "top_k": 3}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)



