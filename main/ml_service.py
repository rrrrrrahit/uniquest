"""
Модуль машинного обучения и ИИ для анализа успеваемости студентов
Прогнозирование проблемных тем и рекомендации
"""
import numpy as np
from django.db.models import Avg, Count
from .models import Grade, StudentProgress, ProblemPrediction, Submission
from decimal import Decimal
import json


def predict_student_performance(student, course):
    """
    Прогнозирует успеваемость студента на основе его истории оценок
    Использует простой алгоритм машинного обучения
    """
    grades = Grade.objects.filter(student=student, course=course).order_by('date')
    
    if grades.count() < 3:
        return None
    
    scores = [float(g.value) for g in grades]
    
    # Простой прогноз на основе тренда
    x = np.arange(len(scores))
    if len(scores) > 1:
        trend = np.polyfit(x, scores, 1)[0]  # Линейный тренд
        predicted_score = scores[-1] + trend * 2  # Прогноз на 2 шага вперед
        predicted_score = max(0, min(100, predicted_score))  # Ограничиваем 0-100
    else:
        predicted_score = scores[0]
    
    # Анализ проблемных тем
    topic_scores = {}
    for grade in grades:
        topic = grade.topic or 'Общее'
        if topic not in topic_scores:
            topic_scores[topic] = []
        topic_scores[topic].append(float(grade.value))
    
    problem_areas = []
    for topic, scores_list in topic_scores.items():
        avg_score = np.mean(scores_list)
        if avg_score < 60:
            problem_areas.append({
                'topic': topic,
                'avg_score': round(avg_score, 2),
                'severity': 'high' if avg_score < 50 else 'medium',
                'count': len(scores_list)
            })
    
    # Уверенность прогноза (чем больше данных, тем выше уверенность)
    confidence = min(100, 30 + len(scores) * 10)
    
    # Рекомендации на основе анализа
    recommendations = []
    overall_avg = np.mean(scores)
    
    if overall_avg < 60:
        recommendations.append(f"Средний балл по курсу низкий ({overall_avg:.1f}). Рекомендуется усиленная подготовка.")
    
    if len(problem_areas) > 0:
        topics_list = ', '.join([pa['topic'] for pa in problem_areas[:3]])
        recommendations.append(f"Проблемные темы: {topics_list}. Необходимо дополнительное изучение.")
    
    if trend < -5:
        recommendations.append("Замечено снижение успеваемости. Рекомендуется консультация с преподавателем.")
    elif trend > 5:
        recommendations.append("Положительная динамика! Продолжайте в том же духе.")
    
    if not recommendations:
        recommendations.append("Успеваемость стабильная. Продолжайте поддерживать текущий уровень.")
    
    return {
        'predicted_score': round(predicted_score, 2),
        'problem_areas': problem_areas,
        'recommendations': recommendations,
        'confidence': round(confidence, 2),
        'overall_avg': round(overall_avg, 2),
        'trend': 'down' if trend < -5 else 'up' if trend > 5 else 'stable'
    }


def analyze_submission(submission):
    """
    Анализирует работу студента и создает прогноз проблем
    """
    if not submission:
        return None
    
    student = submission.student
    course = submission.assignment.course
    
    # Получаем все оценки студента по этому курсу
    grades = Grade.objects.filter(student=student, course=course)
    
    if grades.exists():
        avg_score = grades.aggregate(avg=Avg('value'))['avg']
        predicted_score = float(avg_score) if avg_score else 70.0
    else:
        # Если нет оценок, используем средний по группе
        course_grades = Grade.objects.filter(course=course)
        if course_grades.exists():
            avg_group_score = course_grades.aggregate(avg=Avg('value'))['avg']
            predicted_score = float(avg_group_score) if avg_group_score else 70.0
        else:
            predicted_score = 70.0
    
    # Определяем уровень сложности задания на основе типа
    difficulty_map = {
        'homework': 'low',
        'quiz': 'medium',
        'lab': 'medium',
        'project': 'high',
        'exam': 'high'
    }
    difficulty_level = difficulty_map.get(submission.assignment.assignment_type, 'medium')
    
    # Анализ проблемных областей (на основе темы задания)
    problem_areas = []
    if submission.assignment.topic:
        topic_grades = grades.filter(topic=submission.assignment.topic)
        if topic_grades.exists():
            topic_avg = topic_grades.aggregate(avg=Avg('value'))['avg']
            if topic_avg and float(topic_avg) < 60:
                problem_areas.append(submission.assignment.topic)
    
    # Рекомендации
    recommendations = []
    if predicted_score < 70:
        recommendations.append(f"Ожидаемый балл: {predicted_score:.1f}. Рекомендуется тщательная подготовка.")
    
    if difficulty_level == 'high':
        recommendations.append("Задание высокой сложности. Уделите достаточно времени на выполнение.")
    
    if len(problem_areas) > 0:
        recommendations.append(f"Проблемные темы: {', '.join(problem_areas)}. Повторите материал перед выполнением.")
    
    # Создаем или обновляем прогноз
    prediction, created = ProblemPrediction.objects.get_or_create(
        submission=submission,
        defaults={
            'predicted_score': Decimal(str(predicted_score)),
            'difficulty_level': difficulty_level,
            'problem_areas': problem_areas,
            'recommendations': ' '.join(recommendations) if recommendations else 'Работа выполнена хорошо.',
            'confidence': 75.0,
        }
    )
    
    return prediction


def get_class_performance_statistics(course):
    """
    Получает статистику успеваемости всего класса
    """
    grades = Grade.objects.filter(course=course)
    
    if not grades.exists():
        return None
    
    students_count = grades.values('student').distinct().count()
    avg_score = grades.aggregate(avg=Avg('value'))['avg']
    
    # Распределение по оценкам
    excellent = grades.filter(value__gte=90).count()
    good = grades.filter(value__gte=80, value__lt=90).count()
    average = grades.filter(value__gte=70, value__lt=80).count()
    poor = grades.filter(value__lt=70).count()
    
    # Проблемные темы для класса
    topic_stats = {}
    for grade in grades:
        topic = grade.topic or 'Общее'
        if topic not in topic_stats:
            topic_stats[topic] = {'total': 0, 'sum': 0}
        topic_stats[topic]['total'] += 1
        topic_stats[topic]['sum'] += float(grade.value)
    
    problem_topics = []
    for topic, stats in topic_stats.items():
        avg = stats['sum'] / stats['total']
        if avg < 60 and stats['total'] >= 3:
            problem_topics.append({
                'topic': topic,
                'avg_score': round(avg, 2),
                'students_affected': stats['total']
            })
    
    return {
        'students_count': students_count,
        'avg_score': round(float(avg_score), 2) if avg_score else 0,
        'distribution': {
            'excellent': excellent,
            'good': good,
            'average': average,
            'poor': poor
        },
        'problem_topics': sorted(problem_topics, key=lambda x: x['avg_score'])[:5]
    }


def recommend_study_plan(student, course):
    """
    Рекомендует план обучения для студента на основе его успеваемости
    """
    grades = Grade.objects.filter(student=student, course=course).order_by('date')
    
    if grades.count() < 2:
        return {
            'plan': 'Нормальный',
            'recommendations': ['Начните изучение курса. Регулярно посещайте занятия.']
        }
    
    scores = [float(g.value) for g in grades]
    recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else np.mean(scores)
    overall_avg = np.mean(scores)
    
    if recent_avg < 60:
        return {
            'plan': 'Интенсивный',
            'recommendations': [
                'Увеличьте время на изучение материала',
                'Посещайте дополнительные консультации',
                'Выполняйте все домашние задания',
                'Повторите пройденные темы'
            ]
        }
    elif recent_avg < 75:
        return {
            'plan': 'Стандартный',
            'recommendations': [
                'Поддерживайте текущий темп обучения',
                'Не пропускайте занятия',
                'Своевременно сдавайте задания'
            ]
        }
    else:
        return {
            'plan': 'Поддерживающий',
            'recommendations': [
                'Продолжайте в том же духе',
                'Можете помогать другим студентам',
                'Рассмотрите дополнительные задания для углубления знаний'
            ]
        }

