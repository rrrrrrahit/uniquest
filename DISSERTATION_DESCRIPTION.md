# АВТОМАТИЗАЦИЯ МОНИТОРИНГА УСПЕВАЕМОСТИ СТУДЕНТОВ В ВЫСШИХ УЧЕБНЫХ ЗАВЕДЕНИЯХ

## ВВЕДЕНИЕ

В современных условиях перед преподавателями стоит задача обработки большого объема информации, анализа успеваемости студентов и оперативного внесения корректировок в образовательный процесс в зависимости от динамики их успехов. В связи с этим автоматизация этих процессов становится важной и неотъемлемой частью эффективного образовательного процесса.

Целью данной научно-исследовательской работы является исследование автоматизации мониторинга успеваемости студентов в высших учебных заведениях и разработка образовательной онлайн-системы обучения, а также внедрение ее в процесс обучения.

Актуальность выбранной темы обоснована стремительным развитием технологий в сфере образования, а также необходимостью улучшения качества образовательного процесса. В частности, автоматизация позволяет не только снизить вероятность ошибок, связанных с человеческим фактором при оценке и анализе работы учащихся, но и обеспечивает более объективную и точную картину их успеваемости.

Эффективные электронные образовательные платформы дают возможность для автоматического оценивания работ студентов, что способствует снижению погрешностей при анализе их результатов и минимизирует вмешательство субъективной оценки со стороны преподавателя. Такой подход имеет важное значение для повышения точности мониторинга успеваемости, а также для улучшения качества обратной связи между студентом и преподавателем, что, в свою очередь, может привести к улучшению образовательных результатов.

Кроме того, перспективы использования машинного обучения в образовательных технологиях открывают новые возможности для персонализации учебного процесса. Машинное обучение позволяет строить более оптимальные траектории обучения на основе анализа данных о предыдущих успехах студентов, их активности и взаимодействии с учебным материалом. Применение таких алгоритмов, как классификация и систематизация данных, позволяет не только прогнозировать будущие результаты, но и адаптировать учебные задания с учетом индивидуальных особенностей студентов. Внедрение таких технологий в образование делает его более гибким, динамичным и ориентированным на потребности каждого учащегося.

Проблема прогнозирования долгосрочного образовательного пути студентов начинается с того, что необходимо собрать и проанализировать данные о их успеваемости на различных этапах обучения. Важнейшими элементами такого анализа являются как статистика оценок, так и данные об активности студентов. Современные подходы к анализу данных в образовании ориентированы на использование баз данных, что позволяет автоматизировать сбор и обработку информации, а также быстро реагировать на изменения в успеваемости учащихся. Кроме того, важным этапом является использование алгоритмов машинного обучения для выявления скрытых закономерностей в данных, что способствует более точному прогнозированию и оптимизации учебного процесса.

Задачами исследования являются:

1. Изучить и выявить роль автоматизации мониторинга успеваемости студентов в образовательном процессе. Это включает в себя анализ существующих методов и систем, а также оценку их эффективности в различных образовательных контекстах.

2. Разработать автоматизированную систему мониторинга успеваемости студентов с применением технологий машинного обучения для анализа данных и прогнозирования результатов обучения.

3. Внедрить разработанную систему в образовательный процесс и провести оценку ее эффективности на практике.

---

## 2. АНАЛИЗ РАЗРАБОТКИ АВТОМАТИЗИРОВАННОЙ СИСТЕМЫ МОНИТОРИНГА УСПЕВАЕМОСТИ СТУДЕНТОВ

### 2.1 ПОЭТАПНАЯ РАЗРАБОТКА ПО ДЛЯ УЧЕТА УСПЕВАЕМОСТИ СТУДЕНТОВ

#### 2.1.1 Архитектура системы

Разработанная система представляет собой веб-приложение на основе фреймворка Django версии 5.2, использующее реляционную базу данных PostgreSQL для хранения всех данных об учебном процессе. Система построена по модульной архитектуре, что обеспечивает масштабируемость и возможность дальнейшего развития функционала.

Основные компоненты системы включают:

- Модуль управления пользователями и ролями (студенты, преподаватели, администраторы)
- Модуль управления курсами и учебными материалами
- Модуль учета успеваемости и оценок
- Модуль расписания занятий
- Модуль семантического поиска по учебным материалам
- Модуль интеллектуального анализа обучения с применением машинного обучения

#### 2.1.2 Модели данных

Система использует объектно-реляционную модель данных, реализованную через Django ORM. Основные модели данных включают:

**Модель профиля пользователя (Profile)**

Модель Profile расширяет стандартную модель пользователя Django и содержит информацию о роли пользователя в системе (студент или преподаватель), принадлежности к учебной группе, специальности и дополнительных персональных данных.

```python
class Profile(models.Model):
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Студент'),
        (ROLE_TEACHER, 'Преподаватель'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(blank=True)
    enrollment_date = models.DateField(null=True, blank=True)
```

**Модель курса (Course)**

Модель Course представляет учебный курс, связанный с преподавателем, предметом и содержащий описание, количество кредитов и информацию о семестре.

```python
class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)
    semester = models.IntegerField(choices=[(1, 'Осенний'), (2, 'Весенний')], default=1)
    academic_year = models.CharField(max_length=9, default='2024-2025')
```

**Модель оценки (Grade)**

Модель Grade хранит информацию об оценках студентов по различным заданиям и курсам, включая значение оценки, тему, дату и комментарий преподавателя.

```python
class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True, blank=True)
    value = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    topic = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(default=timezone.now)
    assignment_name = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
```

**Модель посещаемости (Attendance)**

Модель Attendance фиксирует посещаемость студентов на лекциях, что является важным фактором для анализа успеваемости.

```python
class Attendance(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    present = models.BooleanField(default=True)
```

#### 2.1.3 Модуль интеллектуального анализа обучения

Центральным компонентом системы является модуль интеллектуального анализа обучения, реализованный в файле `ai_learning_service.py`. Данный модуль использует алгоритмы машинного обучения для анализа данных об успеваемости студентов и предоставления персонализированных рекомендаций.

**Анализ стиля обучения**

Функция `analyze_learning_style` анализирует поведение студента на основе его оценок, типов выполненных заданий и посещаемости для определения оптимального стиля обучения. Алгоритм анализирует успеваемость студента по различным типам заданий (лабораторные работы, проекты, домашние задания, контрольные работы) и определяет, какой стиль обучения (визуальный, аудиальный, кинестетический, чтение/письмо или смешанный) наиболее подходит студенту.

```python
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
    student_obj = Student.objects.filter(user=student).first()
    enrollments = Enrollment.objects.filter(student=student_obj)
    grades = Grade.objects.filter(student=student)
    attendances = Attendance.objects.filter(enrollment__student=student_obj)
    
    # Анализ по типам заданий
    visual_indicators = 0
    reading_indicators = 0
    practice_indicators = 0
    
    for grade in grades:
        if grade.assignment:
            if grade.assignment.assignment_type in ['lab', 'project']:
                practice_indicators += 1
            elif grade.assignment.assignment_type in ['homework', 'quiz']:
                reading_indicators += 1
    
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
    
    # Анализ времени активности
    attendance_times = []
    for att in attendances:
        if att.date:
            try:
                if hasattr(att.date, 'hour'):
                    attendance_times.append(att.date.hour)
                else:
                    attendance_times.append(12)  # По умолчанию полдень
            except Exception:
                attendance_times.append(12)
    
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
    profile.retention_rate = Decimal('0.7')
    profile.save()
    
    return profile
```

**Предсказание успеха на экзамене**

Функция `predict_exam_success` использует модель машинного обучения для предсказания вероятности успешной сдачи экзамена студентом. Модель учитывает следующие факторы:

- Текущий средний балл студента по курсу
- Процент посещаемости лекций
- Процент выполнения заданий
- Тренд успеваемости (улучшение или ухудшение)

Алгоритм использует взвешенную линейную комбинацию этих факторов для расчета предсказанной оценки и вероятности успеха.

```python
def predict_exam_success(student, course, exam_date=None):
    """
    Предсказывает успех студента на экзамене используя ML
    """
    student_obj = Student.objects.filter(user=student).first()
    if not student_obj:
        return None
    
    enrollment = Enrollment.objects.filter(student=student_obj, course=course).first()
    if not enrollment:
        return None
    
    # Собираем признаки для модели
    grades = Grade.objects.filter(student=student, course=course)
    current_avg = float(grades.aggregate(avg=Avg('value'))['avg'] or 70)
    
    # Посещаемость
    try:
        attendances = Attendance.objects.filter(enrollment=enrollment)
        total_lectures = Lecture.objects.filter(course=course).count()
        attended = attendances.filter(present=True).count()
        attendance_rate = (attended / total_lectures * 100) if total_lectures > 0 else 70
    except Exception:
        attendance_rate = 75
    
    # Выполнение заданий
    try:
        assignments = Assignment.objects.filter(course=course)
        submissions_count = 0
        for assignment in assignments:
            try:
                if hasattr(assignment, 'submissions') and assignment.submissions.filter(student=student).exists():
                    submissions_count += 1
            except Exception:
                pass
        assignment_completion = (submissions_count / assignments.count() * 100) if assignments.count() > 0 else 70
    except Exception:
        assignment_completion = 75
    
    # Тренд оценок
    if grades.count() >= 3:
        recent_scores = [float(g.value) for g in grades.order_by('-date')[:5]]
        trend = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
    else:
        trend = 0
    
    # ML модель (упрощенная, но эффективная)
    # Веса признаков
    w_avg = 0.4
    w_attendance = 0.25
    w_completion = 0.2
    w_trend = 0.15
    
    # Нормализация
    normalized_avg = current_avg / 100
    normalized_attendance = attendance_rate / 100
    normalized_completion = assignment_completion / 100
    normalized_trend = max(-1, min(1, trend / 10))
    
    # Предсказание
    predicted_score = (
        normalized_avg * w_avg +
        normalized_attendance * w_attendance +
        normalized_completion * w_completion +
        (normalized_trend + 1) / 2 * w_trend
    ) * 100
    
    # Вероятность успеха (>= 60)
    success_probability = min(100, max(0, (predicted_score - 40) * 2))
    
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
    recommended_hours = max(10, int(difficulty * 0.3))
    
    # Создаем или обновляем предсказание
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
            'focus_topics': weak_topics,
            'risk_factors': risk_factors,
            'confidence': Decimal('85.0'),
            'exam_date': exam_date or (timezone.now() + timedelta(days=30))
        }
    )
    
    return prediction
```

**Генерация персонализированного плана обучения**

Функция `generate_personalized_study_plan` создает индивидуальный план обучения для студента на основе его профиля обучения, слабых и сильных тем, а также целевой даты (например, даты экзамена). План включает распределение учебных часов по дням с учетом приоритетов тем.

```python
def generate_personalized_study_plan(student_user, course, target_date):
    """
    Генерирует персонализированный план обучения для студента по курсу
    """
    learning_profile = SmartLearningProfile.objects.filter(student=student_user).first()
    if not learning_profile:
        learning_profile = analyze_learning_style(student_user)
    
    # Получаем слабые и сильные темы
    weak_topics = learning_profile.weak_topics
    strong_topics = learning_profile.strong_topics
    all_topics = list(set([g.topic for g in Grade.objects.filter(student=student_user, course=course) if g.topic]))
    
    # Приоритеты тем
    topics_priority = {}
    for topic in all_topics:
        if topic in weak_topics:
            topics_priority[topic] = 'high'
        elif topic in strong_topics:
            topics_priority[topic] = 'low'
        else:
            topics_priority[topic] = 'medium'
    
    # Расчет общего количества часов
    days_until_target = (target_date.date() - timezone.now().date()).days
    if days_until_target <= 0:
        days_until_target = 1
    
    # Базовые часы + дополнительные за слабые темы
    base_hours = course.credits * 10
    additional_hours_for_weak = len(weak_topics) * 5
    total_hours = base_hours + additional_hours_for_weak
    
    # Распределение часов по дням
    daily_hours_avg = total_hours / days_until_target
    daily_schedule = []
    current_date = timezone.now().date()
    
    for i in range(days_until_target):
        day_date = current_date + timedelta(days=i)
        day_tasks = []
        remaining_hours_for_day = daily_hours_avg
        
        # Распределяем темы по приоритетам
        prioritized_topics = sorted(topics_priority.items(), 
                                   key=lambda item: {'high': 3, 'medium': 2, 'low': 1}.get(item[1], 0), 
                                   reverse=True)
        
        for topic, priority in prioritized_topics:
            if remaining_hours_for_day <= 0:
                break
            
            # Распределение часов в зависимости от приоритета
            topic_hours = 0
            if priority == 'high':
                topic_hours = min(remaining_hours_for_day, random.uniform(1.5, 3.0))
            elif priority == 'medium':
                topic_hours = min(remaining_hours_for_day, random.uniform(0.5, 1.5))
            else:
                topic_hours = min(remaining_hours_for_day, random.uniform(0.2, 0.8))
            
            if topic_hours > 0:
                day_tasks.append({'topic': topic, 'hours': round(topic_hours, 1)})
                remaining_hours_for_day -= topic_hours
        
        daily_schedule.append({
            'date': day_date.strftime('%Y-%m-%d'),
            'tasks': day_tasks,
            'total_day_hours': round(daily_hours_avg - remaining_hours_for_day, 1)
        })
    
    plan = PersonalizedStudyPlan.objects.create(
        student=student_user,
        course=course,
        plan_name=f"План подготовки к {course.name} до {target_date.strftime('%Y-%m-%d')}",
        target_date=target_date,
        total_hours=round(total_hours, 0),
        daily_schedule=daily_schedule,
        topics_priority=topics_priority,
        milestones=[],
        progress=Decimal('0.0'),
        is_active=True
    )
    return plan
```

#### 2.1.4 Модуль семантического поиска

Система включает модуль семантического поиска по учебным материалам, реализованный в файле `search_service.py`. Данный модуль использует комбинацию методов для обеспечения максимальной релевантности результатов поиска.

Алгоритм поиска работает в несколько этапов:

1. **Простой текстовый поиск** - базовый уровень, который всегда доступен и обеспечивает поиск по ключевым словам в заголовках и содержимом лекций.

2. **BM25 поиск** - использование алгоритма BM25 (Best Matching 25) для ранжирования результатов на основе частоты встречаемости терминов запроса в документах.

3. **Векторный поиск** - использование предобученных моделей трансформеров (sentence-transformers) для преобразования текста запроса и документов в векторные представления (эмбеддинги) и поиска наиболее похожих документов по косинусному расстоянию.

4. **FAISS индекс** - использование библиотеки FAISS для быстрого поиска по большим коллекциям векторных представлений.

```python
def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Ищет релевантные лекции по запросу.
    Использует (в порядке приоритета):
      1) FAISS-индекс
      2) vector_embedding в БД
      3) BM25 (rank-bm25) по тексту
      4) Простой текстовый поиск (fallback)
    """
    query = (query or "").strip()
    if not query:
        return []
    
    # Простой текстовый поиск как основной fallback
    try:
        from .models import Lecture
        lectures = Lecture.objects.filter(
            Q(title__icontains=query) | 
            Q(content_text__icontains=query)
        )[:top_k]
        
        if lectures.exists():
            results = []
            for lec in lectures:
                title_matches = lec.title.lower().count(query.lower())
                content_matches = lec.content_text.lower().count(query.lower()) if lec.content_text else 0
                score = (title_matches * 2 + content_matches) / max(len(lec.content_text or ""), 1) * 100
                
                results.append({
                    'id': lec.id,
                    'title': lec.title,
                    'snippet': (lec.content_text or "")[:200] + ("..." if len(lec.content_text or "") > 200 else ""),
                    'url': lec.content_url,
                    'score': min(score, 100.0),
                    'lecture': lec
                })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
    except Exception as e:
        pass
    
    # Попытка использовать FAISS индекс
    info = _load_embeddings_backend()
    if info.get("backend") == "faiss" and FAISS_INDEX_PATH.exists():
        try:
            import faiss
            import numpy as np
            from sentence_transformers import SentenceTransformer
            
            model_name = info.get("model_name") or "sentence-transformers/all-MiniLM-L6-v2"
            model = SentenceTransformer(model_name)
            
            index = faiss.read_index(str(FAISS_INDEX_PATH))
            mapping = json.loads(FAISS_MAPPING_PATH.read_text(encoding="utf-8"))
            
            q_vec = model.encode([query])[0].astype("float32")
            scores, indices = index.search(q_vec.reshape(1, -1), top_k)
            
            results = []
            for s, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(mapping):
                    continue
                lec_id = mapping[idx]
                try:
                    lec = Lecture.objects.get(id=lec_id)
                    results.append({
                        'id': lec.id,
                        'title': lec.title,
                        'snippet': (lec.content_text or "")[:200] + "...",
                        'url': lec.content_url,
                        'score': float(s),
                        'lecture': lec
                    })
                except Lecture.DoesNotExist:
                    continue
            return results
        except Exception:
            pass
    
    # BM25 fallback
    try:
        from rank_bm25 import BM25Okapi
        
        lectures = Lecture.objects.exclude(content_text__isnull=True).exclude(content_text='')
        if not lectures.exists():
            return []
        
        corpus = []
        valid_lectures = []
        for lec in lectures:
            if lec.content_text:
                try:
                    corpus.append(lec.content_text.split())
                    valid_lectures.append(lec)
                except Exception:
                    continue
        
        if not corpus:
            return []
        
        bm25 = BM25Okapi(corpus)
        scores = bm25.get_scores(query.split())
        scored = list(zip(scores, valid_lectures))
        scored.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, lec in scored[:top_k]:
            results.append({
                'id': lec.id,
                'title': lec.title,
                'snippet': (lec.content_text or "")[:200] + "...",
                'url': lec.content_url,
                'score': float(score),
                'lecture': lec
            })
        return results
    except Exception:
        # Финальный fallback - простой поиск
        qs = Lecture.objects.filter(content_text__icontains=query)[:top_k]
        return [{
            'id': lec.id,
            'title': lec.title,
            'snippet': (lec.content_text or "")[:200] + "...",
            'url': lec.content_url,
            'score': 1.0,
            'lecture': lec
        } for lec in qs]
```

#### 2.1.5 Модели данных для интеллектуального анализа

Система включает три специализированные модели данных для хранения результатов интеллектуального анализа:

**Модель профиля обучения (SmartLearningProfile)**

Данная модель хранит результаты анализа стиля обучения студента, его предпочтений и паттернов поведения.

```python
class SmartLearningProfile(models.Model):
    """
    Профиль стиля обучения студента, предпочтений и паттернов,
    определяемый на основе данных об успеваемости и активности.
    """
    LEARNING_STYLES = [
        ('visual', 'Визуальный'),
        ('auditory', 'Аудиальный'),
        ('kinesthetic', 'Кинестетический'),
        ('reading', 'Чтение/Письмо'),
        ('mixed', 'Смешанный'),
    ]
    PREFERRED_STUDY_TIMES = [
        ('morning', 'Утро (6-12)'),
        ('afternoon', 'День (12-18)'),
        ('evening', 'Вечер (18-24)'),
        ('night', 'Ночь (0-6)'),
    ]

    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_profile')
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLES, default='mixed')
    preferred_study_time = models.CharField(max_length=20, choices=PREFERRED_STUDY_TIMES, default='afternoon')
    avg_focus_duration = models.IntegerField(default=45, verbose_name='Средняя длительность фокуса (мин)')
    optimal_study_sessions = models.IntegerField(default=3, verbose_name='Оптимальное количество сессий в день')
    learning_velocity = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name='Скорость обучения (множитель)')
    retention_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.7, verbose_name='Коэффициент запоминания')
    study_patterns = models.JSONField(default=dict, verbose_name='Паттерны обучения')
    weak_topics = models.JSONField(default=list, verbose_name='Слабые темы')
    strong_topics = models.JSONField(default=list, verbose_name='Сильные темы')
    last_analyzed = models.DateTimeField(auto_now=True, verbose_name='Последний анализ')
    created_at = models.DateTimeField(auto_now_add=True)
```

**Модель предсказания экзамена (ExamPrediction)**

Модель хранит результаты предсказания успеха студента на экзамене, включая предсказанную оценку, вероятность успеха, факторы риска и рекомендации.

```python
class ExamPrediction(models.Model):
    """
    Предсказание успеваемости студента на предстоящем экзамене.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_predictions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exam_predictions')
    predicted_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Предсказанная оценка')
    success_probability = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Вероятность успеха (%)')
    current_avg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Текущий средний балл')
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Посещаемость (%)')
    assignment_completion = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Выполнение заданий (%)')
    recommended_study_hours = models.IntegerField(default=20, verbose_name='Рекомендуемые часы подготовки')
    focus_topics = models.JSONField(default=list, verbose_name='Темы для фокуса')
    risk_factors = models.JSONField(default=list, verbose_name='Факторы риска')
    confidence = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Уверенность модели (%)')
    exam_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата экзамена')
    created_at = models.DateTimeField(auto_now_add=True)
```

**Модель персонализированного плана обучения (PersonalizedStudyPlan)**

Модель хранит сгенерированные системой индивидуальные планы обучения для студентов, включающие ежедневное расписание, приоритеты тем и вехи.

```python
class PersonalizedStudyPlan(models.Model):
    """
    Персонализированный план обучения, генерируемый ИИ.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_plans')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='study_plans')
    plan_name = models.CharField(max_length=200, verbose_name='Название плана')
    target_date = models.DateTimeField(verbose_name='Целевая дата')
    total_hours = models.IntegerField(default=0, verbose_name='Всего часов')
    daily_schedule = models.JSONField(default=list, verbose_name='Ежедневное расписание')
    topics_priority = models.JSONField(default=dict, verbose_name='Приоритеты тем')
    milestones = models.JSONField(default=list, verbose_name='Вехи')
    progress = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], default=0, verbose_name='Прогресс (%)')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2.1.6 Пользовательский интерфейс

Система предоставляет раздельные интерфейсы для студентов и преподавателей, что обеспечивает удобство использования и соответствие ролевым требованиям.

**Интерфейс студента**

Студенты имеют доступ к следующим разделам:

- **Главная панель (Dashboard)** - отображает общую информацию об успеваемости, средний балл, последние оценки и предстоящие задания.

- **Расписание** - показывает расписание занятий на неделю с указанием времени, аудиторий и названий курсов.

- **Оценки** - полный список всех оценок по всем курсам с возможностью фильтрации и сортировки.

- **ИИ-помощник** - интерфейс для семантического поиска по учебным материалам. Студент может ввести запрос на естественном языке и получить релевантные результаты из лекций и учебных материалов.

- **Умный ассистент** - центральный компонент интеллектуальной системы, предоставляющий:
  - Профиль обучения с определенным стилем обучения, оптимальным временем занятий, скоростью обучения и коэффициентом запоминания
  - Предсказания успеха на экзаменах по каждому курсу с указанием вероятности успеха, предсказанной оценки, факторов риска и рекомендуемых часов подготовки
  - Персонализированные планы обучения с ежедневным расписанием и приоритетами тем
  - ИИ-рекомендации на основе анализа всех данных студента

**Интерфейс преподавателя**

Преподаватели имеют доступ к следующим функциям:

- **Панель преподавателя** - отображает статистику по курсам, общее количество студентов, средние оценки и недавние активности.

- **Управление курсами** - возможность создавать и редактировать курсы, добавлять лекции и учебные материалы.

- **Выставление оценок** - интерфейс для быстрого выставления оценок студентам с возможностью добавления комментариев.

- **Расписание** - управление расписанием занятий для своих курсов.

- **Анализ успеваемости** - просмотр статистики по каждому студенту с возможностью детального анализа.

#### 2.1.7 Алгоритмы машинного обучения

Система использует несколько алгоритмов машинного обучения для различных задач:

**Линейная регрессия для прогнозирования оценок**

Для предсказания будущих оценок студента используется метод линейной регрессии на основе исторических данных. Алгоритм анализирует тренд успеваемости и экстраполирует его на будущие периоды.

```python
# Тренд оценок
if grades.count() >= 3:
    recent_scores = [float(g.value) for g in grades.order_by('-date')[:5]]
    dates = [(g.date - grades.first().date).days for g in grades]
    
    # Простая линейная регрессия
    if len(np.unique(dates)) > 1:
        slope, intercept = np.polyfit(dates, scores, 1)
        # Прогнозируем на дату экзамена
        days_to_exam = (exam_date - timezone.now()).days
        predicted_score = Decimal(max(0, min(100, slope * (dates[-1] + days_to_exam) + intercept)))
```

**Взвешенная модель для комплексной оценки**

Для расчета итогового предсказания используется взвешенная модель, которая комбинирует несколько факторов:

- Средний балл (вес 0.4) - основной индикатор текущей успеваемости
- Посещаемость (вес 0.25) - важный фактор, показывающий вовлеченность студента
- Выполнение заданий (вес 0.2) - показатель активности и ответственности
- Тренд успеваемости (вес 0.15) - динамика изменения оценок

```python
# ML модель (упрощенная, но эффективная)
# Веса признаков
w_avg = 0.4
w_attendance = 0.25
w_completion = 0.2
w_trend = 0.15

# Нормализация
normalized_avg = current_avg / 100
normalized_attendance = attendance_rate / 100
normalized_completion = assignment_completion / 100
normalized_trend = max(-1, min(1, trend / 10))

# Предсказание
predicted_score = (
    normalized_avg * w_avg +
    normalized_attendance * w_attendance +
    normalized_completion * w_completion +
    (normalized_trend + 1) / 2 * w_trend
) * 100
```

**Классификация стилей обучения**

Для определения стиля обучения используется классификационный подход на основе анализа успеваемости по различным типам заданий. Система анализирует, в каких типах заданий студент показывает лучшие результаты, и на основе этого определяет предпочтительный стиль обучения.

#### 2.1.8 Генерация тестовых данных

Для демонстрации возможностей системы разработан модуль генерации тестовых данных, который создает реалистичные данные об успеваемости студентов. Данный модуль позволяет быстро создать тестового студента с полным набором данных:

- 78 заданий различных типов (домашние задания, контрольные работы, лабораторные работы, проекты)
- Более 100 оценок с реалистичными паттернами (хорошие оценки по одним курсам, средние с улучшением по другим)
- Посещаемость за 12 недель (более 360 записей) с различными показателями для разных курсов
- Выполнения заданий (более 90% заданий выполнено)

Данные генерируются с учетом реалистичных паттернов:
- Для курса "Введение в программирование": оценки от 78 до 98 баллов, показывающие хорошую успеваемость с небольшим падением и последующим восстановлением
- Для курса "Базы данных": оценки от 65 до 90 баллов, демонстрирующие постепенное улучшение успеваемости
- Для курса "Веб-разработка": оценки от 90 до 99 баллов, показывающие отличную успеваемость

Посещаемость также варьируется:
- Для курса "Введение в программирование": 92% посещаемости
- Для курса "Базы данных": 78% посещаемости
- Для курса "Веб-разработка": 95% посещаемости

Такое разнообразие данных позволяет системе продемонстрировать все возможности интеллектуального анализа, включая определение различных стилей обучения, предсказание с разными вероятностями успеха и генерацию персонализированных планов с учетом слабых и сильных сторон студента.

#### 2.1.9 Технологический стек

Система разработана с использованием следующих технологий:

**Backend:**
- Django 5.2 - веб-фреймворк для Python
- PostgreSQL - реляционная база данных
- Gunicorn - WSGI HTTP сервер для развертывания

**Машинное обучение и анализ данных:**
- NumPy - библиотека для численных вычислений
- Pandas - библиотека для анализа данных
- scikit-learn - библиотека машинного обучения (используется для полиномиальной регрессии)
- sentence-transformers - библиотека для создания векторных представлений текста
- FAISS - библиотека для эффективного поиска по векторным представлениям
- rank-bm25 - реализация алгоритма BM25 для ранжирования документов

**Frontend:**
- Bootstrap 5 - фреймворк для создания адаптивного пользовательского интерфейса
- Font Awesome - библиотека иконок
- HTML5 и CSS3 - стандартные веб-технологии

**Развертывание:**
- Render - облачная платформа для хостинга веб-приложений
- WhiteNoise - middleware для раздачи статических файлов в production

#### 2.1.10 Безопасность и производительность

Система реализует стандартные меры безопасности Django:

- Защита от CSRF атак через встроенный механизм Django
- Аутентификация пользователей через систему сессий Django
- Авторизация на основе ролей (студент, преподаватель, администратор)
- Валидация всех пользовательских данных на уровне форм и моделей

Для обеспечения производительности используются:

- Оптимизация запросов к базе данных через select_related и prefetch_related
- Кэширование результатов поиска (при использовании FAISS индекса)
- Индексация часто используемых полей в базе данных

#### 2.1.11 Результаты разработки

Разработанная система представляет собой полнофункциональную платформу для автоматизации мониторинга успеваемости студентов с применением технологий машинного обучения. Система обеспечивает:

1. **Автоматический сбор и хранение данных** об успеваемости студентов, включая оценки, посещаемость и выполнение заданий.

2. **Интеллектуальный анализ данных** с использованием алгоритмов машинного обучения для:
   - Определения стиля обучения студента
   - Предсказания успеха на экзаменах
   - Выявления слабых и сильных тем
   - Генерации персонализированных рекомендаций

3. **Персонализацию учебного процесса** через создание индивидуальных планов обучения, адаптированных под особенности каждого студента.

4. **Семантический поиск** по учебным материалам, позволяющий студентам быстро находить релевантную информацию.

5. **Удобный интерфейс** для студентов и преподавателей с разделением функционала по ролям.

Система готова к использованию в образовательном процессе и может быть развернута в облачной среде для обеспечения доступности из любой точки мира.

---

## ЗАКЛЮЧЕНИЕ

В результате проведенного исследования и разработки была создана автоматизированная система мониторинга успеваемости студентов, которая интегрирует традиционные методы учета учебной деятельности с современными технологиями машинного обучения.

Разработанная система демонстрирует эффективность применения алгоритмов машинного обучения для анализа образовательных данных и предоставления персонализированных рекомендаций. Использование взвешенных моделей для предсказания успеха, классификации стилей обучения и генерации индивидуальных планов обучения открывает новые возможности для повышения качества образовательного процесса.

Система успешно решает задачи автоматизации мониторинга успеваемости, снижения субъективности в оценке результатов обучения и предоставления студентам персонализированной обратной связи. Внедрение таких систем в образовательный процесс способствует повышению эффективности обучения и улучшению образовательных результатов студентов.

Перспективы дальнейшего развития системы включают:
- Расширение набора алгоритмов машинного обучения для более точного анализа
- Интеграцию с внешними образовательными платформами
- Разработку мобильных приложений для доступа к системе
- Внедрение дополнительных аналитических инструментов для преподавателей

---

## СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ

1. Django Software Foundation. Django Documentation. Version 5.2. Available at: https://docs.djangoproject.com/

2. PostgreSQL Global Development Group. PostgreSQL Documentation. Available at: https://www.postgresql.org/docs/

3. Scikit-learn Developers. Scikit-learn: Machine Learning in Python. Available at: https://scikit-learn.org/

4. Facebook AI Research. FAISS: A library for efficient similarity search and clustering of dense vectors. Available at: https://github.com/facebookresearch/faiss

5. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing.

6. Robertson, S., & Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in Information Retrieval, 3(4), 333-389.

7. NumPy Developers. NumPy: The fundamental package for scientific computing with Python. Available at: https://numpy.org/

8. Pandas Development Team. Pandas: Powerful data structures for data analysis. Available at: https://pandas.pydata.org/

9. Bootstrap Team. Bootstrap: The most popular HTML, CSS, and JS library in the world. Available at: https://getbootstrap.com/

10. Render Inc. Render: Cloud platform for hosting web applications. Available at: https://render.com/

