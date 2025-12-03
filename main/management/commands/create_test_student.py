from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from main.models import Group, Profile, Student, Course, ScheduleEntry, Enrollment
from datetime import time


class Command(BaseCommand):
    help = 'Создает тестового студента с группой, курсами и расписанием'

    def handle(self, *args, **options):
        # Создаем или получаем группу
        group, created = Group.objects.get_or_create(
            name='CS-101',
            defaults={'year': timezone.now().year}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создана группа: {group.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Используется существующая группа: {group.name}'))

        # Создаем или получаем пользователя
        username = 'test_student'
        password = 'test123456'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'test_student@example.com',
                'first_name': 'Тестовый',
                'last_name': 'Студент',
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Используется существующий пользователь: {username}'))

        # Создаем или обновляем профиль
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'role': Profile.ROLE_STUDENT,
                'group': group,
            }
        )
        if not created:
            profile.group = group
            profile.role = Profile.ROLE_STUDENT
            profile.save()
        
        self.stdout.write(self.style.SUCCESS(f'Профиль создан/обновлен для {username}'))

        # Создаем или получаем студента
        student, created = Student.objects.get_or_create(
            user=user,
            defaults={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'group': group,
            }
        )
        if not created:
            student.group = group
            student.save()
        
        self.stdout.write(self.style.SUCCESS(f'Студент создан/обновлен: {student}'))

        # Создаем тестовые курсы
        courses_data = [
            {'name': 'Введение в программирование', 'code': 'CS101'},
            {'name': 'Базы данных', 'code': 'CS102'},
            {'name': 'Веб-разработка', 'code': 'CS201'},
        ]
        
        courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    'name': course_data['name'],
                    'description': f'Описание курса {course_data["name"]}',
                    'credits': 3,
                }
            )
            courses.append(course)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан курс: {course.name}'))

        # Создаем записи на курсы
        for course in courses:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Студент записан на курс: {course.name}'))

        # Создаем расписание
        schedule_data = [
            {'weekday': 0, 'start_time': '09:00', 'end_time': '10:30', 'course': courses[0]},
            {'weekday': 1, 'start_time': '10:40', 'end_time': '12:10', 'course': courses[1]},
            {'weekday': 2, 'start_time': '13:00', 'end_time': '14:30', 'course': courses[2]},
            {'weekday': 3, 'start_time': '09:00', 'end_time': '10:30', 'course': courses[0]},
            {'weekday': 4, 'start_time': '10:40', 'end_time': '12:10', 'course': courses[1]},
        ]
        
        for sched_data in schedule_data:
            entry, created = ScheduleEntry.objects.get_or_create(
                course=sched_data['course'],
                weekday=sched_data['weekday'],
                start_time=sched_data['start_time'],
                end_time=sched_data['end_time'],
                defaults={'classroom': 'Аудитория 101'}
            )
            if created or not entry.groups.filter(id=profile.id).exists():
                entry.groups.add(profile)
                self.stdout.write(self.style.SUCCESS(
                    f'Добавлено расписание: {sched_data["course"].name} - {entry.get_weekday_display()} {sched_data["start_time"]}'
                ))

        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Тестовый студент создан успешно!'))
        self.stdout.write(self.style.SUCCESS(f'Логин: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Пароль: {password}'))
        self.stdout.write(self.style.SUCCESS('='*50))

