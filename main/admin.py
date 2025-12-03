from django.contrib import admin
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
    list_display = ('user', 'role', 'group', 'specialty', 'phone', 'iin')
    list_filter = ('role', 'specialty', 'group')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'iin', 'phone')

# ----------------- Course -----------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'subject', 'teacher', 'credits', 'semester', 'academic_year')
    list_filter = ('semester', 'academic_year', 'subject', 'teacher')
    search_fields = ('code', 'name')
    ordering = ('-academic_year', 'semester', 'code')

# ----------------- Assignment -----------------
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'assignment_type', 'due_date', 'max_score')
    list_filter = ('assignment_type', 'course')
    search_fields = ('title', 'course__name', 'topic')
    ordering = ('-due_date',)

# ----------------- Submission -----------------
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'score')
    list_filter = ('assignment', 'submitted_at')
    search_fields = ('student__username', 'assignment__title')
    ordering = ('-submitted_at',)

# ----------------- ProblemPrediction -----------------
@admin.register(ProblemPrediction)
class ProblemPredictionAdmin(admin.ModelAdmin):
    list_display = ('submission', 'predicted_score', 'difficulty_level', 'confidence', 'created_at')
    list_filter = ('difficulty_level',)
    search_fields = ('submission__student__username', 'submission__assignment__title')
    ordering = ('-created_at',)

# ----------------- StudentProgress -----------------
@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'topic', 'understanding_level', 'created_at')
    list_filter = ('course', 'understanding_level')
    search_fields = ('student__username', 'topic')
    ordering = ('-created_at',)

# ----------------- Recommendation -----------------
@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('submission', 'topic', 'created_at')
    search_fields = ('submission__student__username', 'topic')
    ordering = ('-created_at',)

# ----------------- ScheduleEntry -----------------
@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ('course', 'weekday', 'start_time', 'end_time', 'classroom')
    list_filter = ('weekday', 'course')
    search_fields = ('course__name', 'classroom')

# ----------------- Student -----------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'group', 'is_active')
    list_filter = ('group', 'is_active')
    search_fields = ('last_name', 'first_name', 'email')
    ordering = ('last_name', 'first_name')

# ----------------- Enrollment -----------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('student__last_name', 'student__first_name', 'course__name')
    ordering = ('-enrolled_at',)

# ----------------- Lecture -----------------
@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'course__name', 'content_text')
    ordering = ('-created_at',)

# ----------------- Attendance -----------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lecture', 'date', 'present')
    list_filter = ('present', 'date')
    search_fields = ('enrollment__student__last_name', 'enrollment__student__first_name')
    ordering = ('-date',)

# ----------------- Grade -----------------
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'assignment', 'value', 'letter_grade', 'date')
    list_filter = ('letter_grade', 'course', 'assignment')
    search_fields = ('student__username', 'course__name', 'assignment__title', 'assignment_name')
    ordering = ('-date',)
