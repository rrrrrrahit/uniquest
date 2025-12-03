from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    Specialty, Subject, Group, Profile, Course, Assignment, Submission,
    ProblemPrediction, StudentProgress, Recommendation, ScheduleEntry,
    Grade, Student, Enrollment, Lecture, Attendance
)

# ----------------- Specialty -----------------
@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_ru', 'name_kk')
    search_fields = ('code', 'name_ru', 'name_kk')
    ordering = ('code',)

# ----------------- Subject -----------------
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_ru', 'name_kk', 'credits', 'specialty')
    list_filter = ('specialty',)
    search_fields = ('code', 'name_ru', 'name_kk')
    ordering = ('code',)

# ----------------- Group -----------------
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'created_at')
    search_fields = ('name',)
    ordering = ('-year', 'name')

# ----------------- Profile -----------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'group', 'specialty')
    list_filter = ('role', 'group', 'specialty')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('user__username',)

# ----------------- Course -----------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'teacher', 'credits', 'semester', 'academic_year')
    list_filter = ('semester', 'academic_year', 'subject')
    search_fields = ('name', 'code')
    ordering = ('-academic_year', 'semester', 'code')

# ----------------- Assignment -----------------
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'assignment_type', 'due_date', 'max_score')
    list_filter = ('assignment_type', 'course')
    search_fields = ('title', 'course__name')
    ordering = ('-due_date',)

# ----------------- Submission -----------------
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'score')
    list_filter = ('assignment__course', 'submitted_at')
    search_fields = ('student__username', 'assignment__title')
    ordering = ('-submitted_at',)

# ----------------- ProblemPrediction -----------------
@admin.register(ProblemPrediction)
class ProblemPredictionAdmin(admin.ModelAdmin):
    list_display = ('submission', 'difficulty_level', 'predicted_score', 'confidence')
    list_filter = ('difficulty_level',)
    ordering = ('-confidence',)

# ----------------- StudentProgress -----------------
@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'topic', 'understanding_level', 'created_at')
    list_filter = ('understanding_level', 'course')
    search_fields = ('student__username', 'topic')
    ordering = ('-created_at',)

# ----------------- Recommendation -----------------
@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('submission', 'topic', 'created_at')
    search_fields = ('topic', 'text')
    ordering = ('-created_at',)

# ----------------- ScheduleEntry -----------------
@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ('course', 'weekday', 'start_time', 'end_time', 'classroom')
    list_filter = ('weekday', 'course')
    search_fields = ('course__name', 'classroom')
    ordering = ('weekday', 'start_time')

# ----------------- Student -----------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'group', 'is_active', 'created_at')
    list_filter = ('group', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name')

# ----------------- Enrollment -----------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('student__first_name', 'student__last_name', 'course__name')
    ordering = ('-enrolled_at',)

# ----------------- Lecture -----------------
@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'content_text', 'course__name')
    ordering = ('-created_at',)

# ----------------- Attendance -----------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lecture', 'date', 'present')
    list_filter = ('present', 'date', 'lecture__course')
    search_fields = ('enrollment__student__first_name', 'enrollment__student__last_name')
    ordering = ('-date',)

# ----------------- Grade -----------------
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'value', 'letter_grade', 'date', 'assignment_name')
    list_filter = ('letter_grade', 'course', 'date')
    search_fields = ('student__username', 'course__name', 'assignment_name', 'topic')
    ordering = ('-date',)

# Кастомная админка для создания тестового студента
class CustomAdminSite(admin.AdminSite):
    site_header = "UniQuest Администрирование"
    site_title = "UniQuest Admin"
    index_title = "Панель управления"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create-test-student/', self.create_test_student_view, name='create_test_student'),
        ]
        return custom_urls + urls

    def create_test_student_view(self, request):
        """Создает тестового студента через админку"""
        if not request.user.is_staff:
            return HttpResponse("Доступ запрещен", status=403)
        
        try:
            from main.models import Group, Profile, Student, Course, ScheduleEntry, Enrollment
            from datetime import time
            
            # Создаем или получаем группу
            group, created = Group.objects.get_or_create(
                name='CS-101',
                defaults={'year': timezone.now().year}
            )
            
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
            
            # Создаем записи на курсы
            for course in courses:
                Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                )
            
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
            
            messages.success(request, f'✅ Тестовый студент создан успешно!<br>Логин: <strong>{username}</strong><br>Пароль: <strong>{password}</strong>')
        except Exception as e:
            messages.error(request, f'Ошибка при создании студента: {str(e)}')
        
        return redirect('admin:index')

# Используем кастомную админку
admin_site = CustomAdminSite(name='admin')

# Регистрируем все модели в кастомной админке
admin_site.register(Specialty, SpecialtyAdmin)
admin_site.register(Subject, SubjectAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Profile, ProfileAdmin)
admin_site.register(Course, CourseAdmin)
admin_site.register(Assignment, AssignmentAdmin)
admin_site.register(Submission, SubmissionAdmin)
admin_site.register(ProblemPrediction, ProblemPredictionAdmin)
admin_site.register(StudentProgress, StudentProgressAdmin)
admin_site.register(Recommendation, RecommendationAdmin)
admin_site.register(ScheduleEntry, ScheduleEntryAdmin)
admin_site.register(Student, StudentAdmin)
admin_site.register(Enrollment, EnrollmentAdmin)
admin_site.register(Lecture, LectureAdmin)
admin_site.register(Attendance, AttendanceAdmin)
admin_site.register(Grade, GradeAdmin)
