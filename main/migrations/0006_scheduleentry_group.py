from django.db import migrations, models
import django.db.models.deletion
from django.db.migrations.operations import RunSQL, SeparateDatabaseAndState


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_rename_main_attend_date_idx_main_attend_date_afda52_idx_and_more"),
    ]

    operations = [
        # Проверяем, существует ли поле group_id, и добавляем только если его нет
        migrations.RunSQL(
            sql="""
                DO $$ 
                BEGIN
                    -- Добавляем поле group_id только если его еще нет
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='main_scheduleentry' AND column_name='group_id'
                    ) THEN
                        ALTER TABLE main_scheduleentry 
                        ADD COLUMN group_id INTEGER NULL 
                        REFERENCES main_group(id) ON DELETE SET NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="-- Reverse migration not needed",
        ),
        # Добавляем поле в состояние Django (для совместимости)
        # Используем SeparateDatabaseAndState чтобы не выполнять SQL операцию
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # В базе данных уже все сделано через RunSQL выше
            ],
            state_operations=[
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
            ],
        ),
    ]



