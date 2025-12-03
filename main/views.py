# ... existing code ...

def create_test_teacher_view(request):
    """Страница для создания тестового учителя с данными"""
    from django.contrib.auth.models import User
    from .models import Course, Group, Student, Enrollment, Assignment, Grade, Lecture, ScheduleEntry
    from datetime import time, timedelta
    import random
    
    if request.method == 'POST':
        try:
            # Создаем или получаем пользователя учителя
            username = 'test_teacher'
            password = 'teacher123456'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': 'test_teacher@uniquest.kz',
                    'first_name': 'Тестовый',
                    'last_name': 'Преподаватель',
                    'is_staff': True,
                }
            )
            
            if created:
                user.set_password(password)
                user.save()
            
            # Создаем или обновляем профиль
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': Profile.ROLE_TEACHER,
                    'bio': 'Тестовый преподаватель для демонстрации функционала',
                }
            )
            if not created:
                profile.role = Profile.ROLE_TEACHER
                profile.save()
            
            # Создаем или получаем группу
            group, _ = Group.objects.get_or_create(
                name='CS-101',
                defaults={'year': timezone.now().year}
            )
            
            # Создаем курсы для учителя
            courses_data = [
                {
                    'name': 'Введение в программирование',
                    'description': 'Базовый курс программирования на Python',
                    'credits': 3,
                    'subject': None,
                },
                {
                    'name': 'Базы данных',
                    'description': 'Изучение SQL и проектирования баз данных',
                    'credits': 4,
                    'subject': None,
                },
                {
                    'name': 'Веб-разработка',
                    'description': 'HTML, CSS, JavaScript и фреймворки',
                    'credits': 3,
                    'subject': None,
                },
            ]
            
            courses = []
            for course_data in courses_data:
                course, created = Course.objects.get_or_create(
                    name=course_data['name'],
                    defaults={
                        'description': course_data['description'],
                        'credits': course_data['credits'],
                        'teacher': user,
                    }
                )
                if not created:
                    course.teacher = user
                    course.save()
                courses.append(course)
            
            # Создаем расписание для курсов
            schedule_data = [
                {'course': courses[0], 'weekday': 1, 'start_time': time(9, 0), 'end_time': time(10, 30), 'classroom': 'А-101'},
                {'course': courses[1], 'weekday': 2, 'start_time': time(11, 0), 'end_time': time(12, 30), 'classroom': 'Б-205'},
                {'course': courses[2], 'weekday': 3, 'start_time': time(14, 0), 'end_time': time(15, 30), 'classroom': 'В-301'},
            ]
            
            for sched_data in schedule_data:
                entry, created = ScheduleEntry.objects.get_or_create(
                    course=sched_data['course'],
                    weekday=sched_data['weekday'],
                    start_time=sched_data['start_time'],
                    defaults=sched_data
                )
                if created and group:
                    entry.groups.add(Profile.objects.filter(group=group).first() or profile)
            
            # Создаем лекции для курсов
            for course in courses:
                for i in range(10):
                    Lecture.objects.get_or_create(
                        course=course,
                        title=f'Лекция {i+1} - {course.name}',
                        defaults={
                            'content_text': f'Подробное содержание лекции {i+1} по курсу {course.name}. Здесь рассматриваются основные концепции и практические примеры.',
                        }
                    )
            
            # Создаем задания для курсов
            assignments_data = []
            for course in courses:
                for hw_num in range(1, 6):
                    assignment, created = Assignment.objects.get_or_create(
                        course=course,
                        title=f'Домашнее задание {hw_num} - {course.name}',
                        defaults={
                            'description': f'Описание задания {hw_num} по курсу {course.name}',
                            'due_date': timezone.now() + timedelta(days=hw_num * 7),
                            'assignment_type': 'homework',
                            'topic': f'Тема {hw_num}',
                            'max_score': 100,
                        }
                    )
                    assignments_data.append(assignment)
            
            # Получаем студентов для создания оценок
            students = Student.objects.all()[:5]  # Берем первых 5 студентов
            
            # Создаем оценки для студентов
            for student in students:
                for course in courses:
                    # Создаем запись на курс
                    enrollment, _ = Enrollment.objects.get_or_create(
                        student=student,
                        course=course,
                        defaults={'enrolled_at': timezone.now()}
                    )
                    
                    # Создаем оценки
                    for assignment in assignments_data:
                        if assignment.course == course:
                            grade_value = random.randint(60, 100)
                            Grade.objects.get_or_create(
                                student=student.user,
                                course=course,
                                assignment=assignment,
                                defaults={
                                    'value': grade_value,
                                    'topic': assignment.topic,
                                    'date': assignment.due_date - timedelta(days=2),
                                    'assignment_name': assignment.title,
                                    'comment': f'Хорошая работа по теме "{assignment.topic}"',
                                }
                            )
            
            messages.success(request, f'Тестовый учитель создан! Логин: {username}, Пароль: {password}')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Ошибка при создании учителя: {str(e)}')
    
    return render(request, 'main/create_test_teacher.html')

# ... existing code ...
