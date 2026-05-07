from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0015_lecturequiz_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="lecturequiz",
            name="max_attempts",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="lecturequiz",
            name="time_limit_minutes",
            field=models.PositiveIntegerField(default=20),
        ),
    ]
