"""
Революционный ИИ-сервис для персонализированного обучения
Включает анализ стиля обучения, предсказание успеха и умное планирование
"""
import numpy as np
import math
from pathlib import Path
from datetime import timedelta
from django.db.models import Avg, Count, Q
from django.utils import timezone
from decimal import Decimal
from .models import (
    Grade, Student, Enrollment, Attendance, Lecture,
    SmartLearningProfile, ExamPrediction, PersonalizedStudyPlan,
    Course, Assignment
)

_GRADE_MODEL_CACHE = None


def _safe_ratio(numerator, denominator, default=0.0):
    return (numerator / denominator) if denominator else default


def _sigmoid(x):
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _load_grade_model_bundle():
    """
    Загружает обученную sklearn-модель прогноза оценки (если доступна).
    Кэшируется в памяти процесса.
    """
    global _GRADE_MODEL_CACHE
    if _GRADE_MODEL_CACHE is not None:
        return _GRADE_MODEL_CACHE

    model_path = Path("models/grade_model.pkl")
    if not model_path.exists():
        _GRADE_MODEL_CACHE = None
        return None
    try:
        import joblib

        bundle = joblib.load(model_path)
        if isinstance(bundle, dict) and bundle.get("model") and bundle.get("scaler"):
            _GRADE_MODEL_CACHE = bundle
            return bundle
    except Exception:
        pass

    _GRADE_MODEL_CACHE = None
    return None


def _collect_prediction_features(student, course, enrollment):
    """
    Формирует расширенный набор признаков для предиктивной аналитики.
    """
    grades = Grade.objects.filter(student=student, course=course).order_by("date")
    current_avg = float(grades.aggregate(avg=Avg("value"))["avg"] or 70.0)

    # Посещаемость.
    try:
        attendances = Attendance.objects.filter(enrollment=enrollment)
        total_lectures = Lecture.objects.filter(course=course).count()
        attended = attendances.filter(present=True).count()
        attendance_rate = _safe_ratio(attended * 100.0, total_lectures, default=70.0)
    except Exception:
        attendance_rate = 70.0

    # Выполнение заданий.
    try:
        assignments = Assignment.objects.filter(course=course)
        assignments_count = assignments.count()
        submissions_count = 0
        for assignment in assignments:
            try:
                if hasattr(assignment, "submissions") and assignment.submissions.filter(student=student).exists():
                    submissions_count += 1
            except Exception:
                continue
        assignment_completion = _safe_ratio(submissions_count * 100.0, assignments_count, default=70.0)
    except Exception:
        assignment_completion = 70.0
        assignments_count = 0
        submissions_count = 0

    # Тренд и волатильность по последним оценкам.
    score_series = [float(g.value) for g in grades]
    if len(score_series) >= 3:
        recent_scores = score_series[-5:]
        trend = float(np.polyfit(range(len(recent_scores)), recent_scores, 1)[0])
        volatility = float(np.std(recent_scores))
    else:
        trend = 0.0
        volatility = 0.0

    # Признаки под сохраненную модель train_grade_model.
    hw_avg = grades.filter(
        Q(assignment_name__icontains="Домаш")
        | Q(assignment_name__icontains="Homework")
        | Q(assignment_name__icontains="homework")
    ).aggregate(avg=Avg("value"))["avg"]
    if hw_avg is None:
        hw_avg = current_avg

    midterm = grades.filter(
        Q(assignment_name__icontains="Midterm")
        | Q(assignment_name__icontains="Мидтерм")
        | Q(assignment_name__icontains="Рубеж")
    ).order_by("-date").first()
    midterm_score = float(midterm.value) if midterm else float(hw_avg)

    previous_gpa = Grade.objects.filter(student=student).exclude(course=course).aggregate(avg=Avg("value"))["avg"]
    previous_gpa = float(previous_gpa) if previous_gpa is not None else float(current_avg)

    data_completeness = np.mean([
        1.0 if grades.count() >= 3 else grades.count() / 3.0,
        min(1.0, _safe_ratio(assignments_count, 4, default=0.0)),
        min(1.0, _safe_ratio(Lecture.objects.filter(course=course).count(), 6, default=0.0)),
    ]) * 100.0

    return {
        "grades": grades,
        "current_avg": float(current_avg),
        "attendance_rate": float(attendance_rate),
        "assignment_completion": float(assignment_completion),
        "trend": float(trend),
        "volatility": float(volatility),
        "hw_avg": float(hw_avg),
        "midterm_score": float(midterm_score),
        "previous_gpa": float(previous_gpa),
        "data_completeness": float(max(0.0, min(100.0, data_completeness))),
    }


def analyze_learning_style(student):
    """
    Анализирует стиль обучения студента на основе его поведения
    Использует ML для определения оптимального способа обучения
    """
    profile, created = SmartLearningProfile.objects.get_or_create(
        student=student,
        defaults={'learning_style': 'mixed'}
    )
    
    # Анализируем паттерны обучения
    try:
        student_obj = Student.objects.filter(user=student).first()
        if not student_obj:
            # Если нет Student объекта, создаем базовый профиль
            profile, created = SmartLearningProfile.objects.get_or_create(
                student=student,
                defaults={'learning_style': 'mixed'}
            )
            return profile
        
        enrollments = Enrollment.objects.filter(student=student_obj)
        grades = Grade.objects.filter(student=student)
        attendances = Attendance.objects.filter(enrollment__student=student_obj)
    except Exception:
        # В случае ошибки создаем базовый профиль
        profile, created = SmartLearningProfile.objects.get_or_create(
            student=student,
            defaults={'learning_style': 'mixed'}
        )
        return profile
    
    # Анализ по типам заданий
    visual_indicators = 0  # Лекции с визуальным контентом
    reading_indicators = 0  # Текстовые материалы
    practice_indicators = 0  # Практические задания
    
    for grade in grades:
        if grade.assignment:
            if grade.assignment.assignment_type in ['lab', 'project']:
                practice_indicators += 1
            elif grade.assignment.assignment_type in ['homework', 'quiz']:
                reading_indicators += 1
    
    # Анализ успеваемости по типам контента
    lecture_grades = []
    assignment_grades = []
    
    for grade in grades:
        if grade.assignment:
            assignment_grades.append(float(grade.value))
        else:
            lecture_grades.append(float(grade.value))
    
    # Определяем стиль на основе данных
    if len(assignment_grades) > 0 and len(lecture_grades) > 0:
        assignment_avg = np.mean(assignment_grades) if assignment_grades else 70
        lecture_avg = np.mean(lecture_grades) if lecture_grades else 70
        
        if assignment_avg > lecture_avg + 5:
            learning_style = 'kinesthetic'  # Лучше практика
        elif lecture_avg > assignment_avg + 5:
            learning_style = 'visual'  # Лучше визуальное
        else:
            learning_style = 'mixed'
    else:
        learning_style = 'mixed'
    
    # Анализ времени активности (на основе посещаемости)
    attendance_times = []
    for att in attendances:
        if att.date:
            # Если date - это date объект, используем время по умолчанию (12:00)
            # Или берем из created_at если есть
            try:
                if hasattr(att.date, 'hour'):
                    attendance_times.append(att.date.hour)
                else:
                    # Если это date объект, используем среднее время (12:00)
                    attendance_times.append(12)
            except Exception:
                attendance_times.append(12)  # По умолчанию полдень
    
    if attendance_times:
        avg_hour = np.mean(attendance_times)
        if 6 <= avg_hour < 12:
            preferred_time = 'morning'
        elif 12 <= avg_hour < 18:
            preferred_time = 'afternoon'
        elif 18 <= avg_hour < 24:
            preferred_time = 'evening'
        else:
            preferred_time = 'night'
    else:
        preferred_time = 'afternoon'
    
    # Вычисляем скорость обучения
    if grades.count() > 0:
        recent_grades = grades.order_by('-date')[:5]
        if recent_grades.count() >= 2:
            scores = [float(g.value) for g in recent_grades]
            trend = np.polyfit(range(len(scores)), scores, 1)[0]
            learning_velocity = max(0.5, min(2.0, 1.0 + trend / 20))
        else:
            learning_velocity = 1.0
    else:
        learning_velocity = 1.0
    
    # Обновляем профиль
    profile.learning_style = learning_style
    profile.preferred_study_time = preferred_time
    profile.learning_velocity = Decimal(str(learning_velocity))
    profile.retention_rate = Decimal('0.7')  # Базовая оценка
    profile.save()
    
    return profile


def predict_exam_success(student, course, exam_date=None):
    """
    Предсказывает успех студента на экзамене используя ML
    """
    # Получаем данные студента
    student_obj = Student.objects.filter(user=student).first()
    if not student_obj:
        return None
    
    enrollment = Enrollment.objects.filter(student=student_obj, course=course).first()
    if not enrollment:
        return None
    
    features = _collect_prediction_features(student, course, enrollment)
    grades = features["grades"]
    current_avg = features["current_avg"]
    attendance_rate = features["attendance_rate"]
    assignment_completion = features["assignment_completion"]
    trend = features["trend"]
    volatility = features["volatility"]
    data_completeness = features["data_completeness"]

    # 1) Основной предиктор: обученная sklearn-модель (если артефакт доступен)
    # 2) Fallback: интерпретируемая эвристика с учетом волатильности.
    predicted_score = None
    bundle = _load_grade_model_bundle()
    model_source = "fallback"
    if bundle:
        try:
            model = bundle["model"]
            scaler = bundle["scaler"]
            x = np.array([[
                features["attendance_rate"],
                features["hw_avg"],
                features["midterm_score"],
                features["previous_gpa"],
            ]], dtype=float)
            x_scaled = scaler.transform(x)
            predicted_score = float(model.predict(x_scaled)[0])
            model_source = "trained_ml"
        except Exception:
            predicted_score = None

    if predicted_score is None:
        normalized_avg = current_avg / 100.0
        normalized_attendance = attendance_rate / 100.0
        normalized_completion = assignment_completion / 100.0
        normalized_trend = max(-1.0, min(1.0, trend / 10.0))
        normalized_volatility = max(0.0, min(1.0, volatility / 20.0))
        predicted_score = (
            normalized_avg * 0.38
            + normalized_attendance * 0.24
            + normalized_completion * 0.22
            + ((normalized_trend + 1.0) / 2.0) * 0.16
            - normalized_volatility * 0.08
        ) * 100.0
        model_source = "fallback"

    predicted_score = max(0.0, min(100.0, predicted_score))

    # Гибридная вероятность успеха:
    # - логистическое преобразование по запасу к порогу;
    # - штраф за высокую волатильность.
    score_margin = (predicted_score - 60.0) / 8.0
    base_success_prob = _sigmoid(score_margin) * 100.0
    volatility_penalty = min(18.0, volatility * 0.9)
    success_probability = max(0.0, min(100.0, base_success_prob - volatility_penalty))
    
    # Определяем факторы риска
    risk_factors = []
    if current_avg < 60:
        risk_factors.append("Низкий средний балл")
    if attendance_rate < 70:
        risk_factors.append("Низкая посещаемость")
    if assignment_completion < 70:
        risk_factors.append("Неполное выполнение заданий")
    if trend < -2:
        risk_factors.append("Снижающаяся успеваемость")
    if volatility > 12:
        risk_factors.append("Высокая волатильность оценок")
    if data_completeness < 60:
        risk_factors.append("Недостаточная полнота данных")
    
    # Темы для фокуса (слабые темы)
    weak_topics = []
    topic_grades = {}
    for grade in grades:
        topic = grade.topic or 'Общее'
        if topic not in topic_grades:
            topic_grades[topic] = []
        topic_grades[topic].append(float(grade.value))
    
    for topic, scores in topic_grades.items():
        if np.mean(scores) < 60:
            weak_topics.append(topic)
    
    # Рекомендуемые часы
    difficulty = 100 - predicted_score
    recommended_hours = max(10, int(difficulty * 0.32 + max(0.0, volatility - 8.0) * 0.8))

    # Уверенность зависит от полноты данных и источника модели.
    model_bonus = 8.0 if bundle else 0.0
    confidence = max(45.0, min(97.0, 50.0 + data_completeness * 0.35 + model_bonus - volatility * 0.4))
    
    # Создаем или обновляем предсказание
    risk_factors_with_meta = list(risk_factors)
    risk_factors_with_meta.insert(0, f"__MODEL_SOURCE__:{model_source}")
    risk_factors_with_meta.insert(1, f"__DATA_COMPLETENESS__:{round(data_completeness, 1)}")
    risk_factors_with_meta.insert(2, f"__VOLATILITY__:{round(volatility, 2)}")

    prediction, created = ExamPrediction.objects.update_or_create(
        student=student,
        course=course,
        defaults={
            'predicted_score': Decimal(str(predicted_score)),
            'success_probability': Decimal(str(success_probability)),
            'current_avg': Decimal(str(current_avg)),
            'attendance_rate': Decimal(str(attendance_rate)),
            'assignment_completion': Decimal(str(assignment_completion)),
            'recommended_study_hours': recommended_hours,
            'focus_topics': weak_topics[:5],
            'risk_factors': risk_factors_with_meta,
            'confidence': Decimal(str(round(confidence, 2))),
            'exam_date': exam_date,
        }
    )
    
    return prediction


def create_personalized_study_plan(student, course, target_date):
    """
    Создает персонализированный план обучения с помощью ИИ
    """
    # Анализируем профиль обучения
    profile = analyze_learning_style(student)
    
    # Получаем предсказание
    prediction = predict_exam_success(student, course, target_date)
    
    # Определяем темы курса
    lectures = Lecture.objects.filter(course=course)
    assignments = Assignment.objects.filter(course=course)
    
    # Анализируем сложность тем
    grades = Grade.objects.filter(student=student, course=course)
    topic_difficulty = {}
    
    for grade in grades:
        topic = grade.topic or 'Общее'
        if topic not in topic_difficulty:
            topic_difficulty[topic] = []
        topic_difficulty[topic].append(float(grade.value))
    
    # Приоритеты тем (сложные темы = высокий приоритет)
    topics_priority = {}
    for topic, scores in topic_difficulty.items():
        avg_score = np.mean(scores) if scores else 70
        priority = max(1, int((100 - avg_score) / 10))  # 1-10
        topics_priority[topic] = priority
    
    # Если нет оценок, используем равномерное распределение
    if not topics_priority:
        for lecture in lectures:
            topics_priority[lecture.title] = 5
    
    # Вычисляем дни до экзамена
    days_until = (target_date - timezone.now()).days
    if days_until < 1:
        days_until = 7  # Минимум неделя
    
    # Рекомендуемые часы (из предсказания или расчет)
    if prediction:
        total_hours = prediction.recommended_study_hours
    else:
        total_hours = max(20, days_until * 2)
    
    # Создаем ежедневное расписание
    daily_schedule = []
    hours_per_day = total_hours / days_until
    
    # Учитываем стиль обучения
    if profile.learning_style == 'visual':
        session_duration = 45  # Визуалы - средние сессии
    elif profile.learning_style == 'kinesthetic':
        session_duration = 30  # Кинестетики - короткие активные сессии
    elif profile.learning_style == 'reading':
        session_duration = 60  # Читатели - длинные сессии
    else:
        session_duration = 45
    
    sessions_per_day = max(1, int(hours_per_day * 60 / session_duration))
    
    # Распределяем темы по дням
    sorted_topics = sorted(topics_priority.items(), key=lambda x: x[1], reverse=True)
    
    for day in range(days_until):
        day_date = timezone.now() + timedelta(days=day)
        day_schedule = {
            'date': day_date.strftime('%Y-%m-%d'),
            'sessions': [],
            'topics': []
        }
        
        # Выбираем темы для дня
        topics_for_day = []
        for i, (topic, priority) in enumerate(sorted_topics):
            if i % days_until == day % len(sorted_topics) if sorted_topics else 0:
                topics_for_day.append(topic)
        
        # Создаем сессии
        for session_num in range(sessions_per_day):
            session = {
                'time': f"{9 + session_num * 3}:00",  # Начало сессии
                'duration': session_duration,
                'topic': topics_for_day[session_num % len(topics_for_day)] if topics_for_day else 'Повторение',
                'type': 'study'
            }
            day_schedule['sessions'].append(session)
        
        day_schedule['topics'] = topics_for_day[:3]  # Топ-3 темы дня
        daily_schedule.append(day_schedule)
    
    # Вехи
    milestones = []
    quarter = days_until // 4
    for i in range(1, 5):
        milestone_date = timezone.now() + timedelta(days=quarter * i)
        milestones.append({
            'date': milestone_date.strftime('%Y-%m-%d'),
            'goal': f"Завершить {i * 25}% подготовки",
            'topics': [t[0] for t in sorted_topics[:i * len(sorted_topics) // 4]]
        })
    
    # Создаем план
    plan, created = PersonalizedStudyPlan.objects.update_or_create(
        student=student,
        course=course,
        target_date=target_date,
        defaults={
            'plan_name': f"План подготовки к {course.name}",
            'total_hours': total_hours,
            'daily_schedule': daily_schedule,
            'topics_priority': topics_priority,
            'milestones': milestones,
            'progress': Decimal('0'),
            'is_active': True,
        }
    )
    
    return plan


def get_ai_recommendations(student, course):
    """
    Получает ИИ-рекомендации для студента по курсу
    """
    recommendations = []
    
    try:
        profile = analyze_learning_style(student)
        
        # Рекомендации на основе стиля обучения
        if profile and profile.learning_style == 'visual':
            recommendations.append({
                'type': 'style',
                'title': 'Визуальный стиль обучения',
                'text': 'Используйте диаграммы, схемы и визуальные материалы для лучшего запоминания.',
                'icon': 'fa-eye'
            })
        elif profile and profile.learning_style == 'kinesthetic':
            recommendations.append({
                'type': 'style',
                'title': 'Кинестетический стиль',
                'text': 'Практикуйтесь активно: решайте задачи, создавайте проекты, экспериментируйте.',
                'icon': 'fa-hands'
            })
        
        # Рекомендации по времени
        if profile and profile.preferred_study_time:
            time_map = {
                'morning': 'Утренние часы (6-12)',
                'afternoon': 'Дневное время (12-18)',
                'evening': 'Вечерние часы (18-24)',
                'night': 'Ночное время (0-6)'
            }
            recommendations.append({
                'type': 'time',
                'title': 'Оптимальное время обучения',
                'text': f'Ваше продуктивное время: {time_map.get(profile.preferred_study_time, "День")}',
                'icon': 'fa-clock'
            })

        # Рекомендации по скорости обучения
        if profile and profile.learning_velocity:
            velocity = float(profile.learning_velocity)
            if velocity < 0.9:
                velocity_text = 'Рекомендуется режим микро-сессий: 25-30 минут учебы и 5 минут перерыва.'
            elif velocity > 1.2:
                velocity_text = 'Можно использовать интенсивные блоки 60-90 минут с контрольными мини-тестами.'
            else:
                velocity_text = 'Поддерживайте стабильный темп: 45-60 минут и краткое закрепление материала.'
            recommendations.append({
                'type': 'velocity',
                'title': 'Скорость обучения',
                'text': velocity_text,
                'icon': 'fa-gauge-high'
            })
    except Exception:
        pass
    
    try:
        prediction = predict_exam_success(student, course)
        
        # Рекомендации на основе предсказания
        if prediction:
            if float(prediction.success_probability) < 70:
                recommendations.append({
                    'type': 'warning',
                    'title': 'Требуется внимание',
                    'text': f'Вероятность успеха: {prediction.success_probability}%. Рекомендуется {prediction.recommended_study_hours} часов подготовки.',
                    'icon': 'fa-exclamation-triangle'
                })
            
            if prediction.focus_topics and len(prediction.focus_topics) > 0:
                focus_topics_str = ", ".join(str(t) for t in prediction.focus_topics[:3])
                recommendations.append({
                    'type': 'focus',
                    'title': 'Темы для фокуса',
                    'text': f'Сосредоточьтесь на: {focus_topics_str}',
                    'icon': 'fa-bullseye'
                })

            # Фактор посещаемости с источником данных мониторинга
            attendance_rate = float(prediction.attendance_rate or 0)
            recommendations.append({
                'type': 'attendance',
                'title': 'Посещаемость (САПА)',
                'text': (
                    f'Текущая посещаемость: {attendance_rate:.1f}%. '
                    'Показатель формируется на основе мониторинга посещаемости '
                    'системой "САПА" (камеры в лекционных аудиториях АТУ).'
                ),
                'icon': 'fa-video'
            })
    except Exception:
        pass
    
    # Если нет рекомендаций, добавляем общие
    if not recommendations:
        recommendations.append({
            'type': 'info',
            'title': 'Начните обучение',
            'text': 'Выполняйте задания и посещайте лекции, чтобы получить персонализированные рекомендации.',
            'icon': 'fa-info-circle'
        })
    
    return recommendations

