from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_rename_main_attend_date_idx_main_attend_date_afda52_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="scheduleentry",
            name="group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="schedule_entries",
                to="main.group",
                verbose_name="Учебная группа",
            ),
        ),
    ]



