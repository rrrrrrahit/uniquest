from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0008_remove_scheduleentry_group_examprediction_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="lecture",
            name="lecture_file",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="lectures/",
                verbose_name="Файл лекции",
            ),
        ),
    ]

