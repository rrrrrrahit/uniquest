from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0016_lecturequiz_limits"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="lecturequizattempt",
            unique_together=set(),
        ),
    ]
