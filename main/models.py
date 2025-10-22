from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_TEACHER, 'Teacher'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    group = models.CharField(max_length=50, blank=True)  # учебная группа (для студентов)

    def __str__(self):
        return f"{self.user.username} Profile"

class Course(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teaching_courses')
    image = models.ImageField(upload_to='courses/', blank=True, null=True)

    def __str__(self):
        return self.title

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=4, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} : {self.grade}"

class ScheduleEntry(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    weekday = models.CharField(max_length=10)  # например: Monday
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100, blank=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['weekday', 'start_time']

    def __str__(self):
        return f"{self.course.title} on {self.weekday} {self.start_time}"
