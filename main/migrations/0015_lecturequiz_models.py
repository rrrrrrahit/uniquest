from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0014_group_course_year"),
    ]

    operations = [
        migrations.CreateModel(
            name="LectureQuiz",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("source_text", models.TextField(blank=True)),
                ("question_count", models.PositiveIntegerField(default=5)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("assignment", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="lecture_quiz", to="main.assignment")),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lecture_quizzes", to="main.course")),
                ("generated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("lecture", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="generated_quizzes", to="main.lecture")),
            ],
            options={
                "verbose_name": "Тест по лекции",
                "verbose_name_plural": "Тесты по лекциям",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="LectureQuizQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_text", models.TextField()),
                ("option_a", models.CharField(max_length=500)),
                ("option_b", models.CharField(max_length=500)),
                ("option_c", models.CharField(max_length=500)),
                ("option_d", models.CharField(max_length=500)),
                ("correct_option", models.CharField(choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")], max_length=1)),
                ("order", models.PositiveIntegerField(default=1)),
                ("quiz", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="main.lecturequiz")),
            ],
            options={
                "verbose_name": "Вопрос теста",
                "verbose_name_plural": "Вопросы теста",
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="LectureQuizAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("total_questions", models.PositiveIntegerField(default=0)),
                ("answers", models.JSONField(blank=True, default=dict)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("quiz", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="main.lecturequiz")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lecture_quiz_attempts", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Попытка теста",
                "verbose_name_plural": "Попытки тестов",
                "ordering": ["-submitted_at"],
                "unique_together": {("quiz", "student")},
            },
        ),
    ]
