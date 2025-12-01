from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Profile, Specialty, Subject, Course, Assignment, Submission,
    Recommendation, ScheduleEntry, Grade, ProblemPrediction, StudentProgress
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'group', 'specialty', 'phone')
    list_filter = ('role', 'specialty')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'group')


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_ru', 'name_kk')
    search_fields = ('code', 'name_ru', 'name_kk')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_ru', 'credits', 'specialty')
    list_filter = ('specialty', 'credits')
    search_fields = ('code', 'name_ru', 'name_kk')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'teacher', 'subject', 'semester', 'academic_year')
    list_filter = ('semester', 'academic_year', 'subject')
    search_fields = ('name', 'code', 'teacher__username')
    raw_id_fields = ('teacher', 'subject')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'assignment_type', 'due_date', 'max_score')
    list_filter = ('assignment_type', 'due_date')
    search_fields = ('title', 'course__name')
    raw_id_fields = ('course',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'score')
    list_filter = ('submitted_at',)
    search_fields = ('student__username', 'assignment__title')
    raw_id_fields = ('student', 'assignment')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'value', 'letter_grade', 'date', 'topic')
    list_filter = ('letter_grade', 'date', 'course')
    search_fields = ('student__username', 'course__name', 'topic')
    raw_id_fields = ('student', 'course', 'assignment')
    date_hierarchy = 'date'


@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ('course', 'weekday', 'start_time', 'end_time', 'classroom')
    list_filter = ('weekday',)
    search_fields = ('course__name', 'classroom')
    raw_id_fields = ('course',)
    filter_horizontal = ('groups',)


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'topic', 'understanding_level', 'created_at')
    list_filter = ('understanding_level', 'created_at')
    search_fields = ('student__username', 'course__name', 'topic')
    raw_id_fields = ('student', 'course')
    date_hierarchy = 'created_at'


@admin.register(ProblemPrediction)
class ProblemPredictionAdmin(admin.ModelAdmin):
    list_display = ('submission', 'predicted_score', 'difficulty_level', 'confidence', 'created_at')
    list_filter = ('difficulty_level', 'created_at')
    search_fields = ('submission__student__username',)
    raw_id_fields = ('submission',)
    date_hierarchy = 'created_at'


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('submission', 'topic', 'created_at')
    search_fields = ('submission__student__username', 'topic')
    raw_id_fields = ('submission',)
    date_hierarchy = 'created_at'
