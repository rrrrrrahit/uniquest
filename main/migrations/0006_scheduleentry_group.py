from django.db import migrations, models
import django.db.models.deletion
from django.db.migrations.operations import RunSQL, RunPython


def add_group_field_state(apps, schema_editor):
    """Обновляем состояние Django, добавляя поле group в модель ScheduleEntry"""
    ScheduleEntry = apps.get_model('main', 'ScheduleEntry')
    Group = apps.get_model('main', 'Group')
    
    # Добавляем поле в состояние модели (не выполняет SQL)
    field = models.ForeignKey(
        Group,
        on_delete=django.db.models.deletion.SET_NULL,
        null=True,
        blank=True,
        related_name='schedule_entries',
        verbose_name='Учебная группа',
    )
    field.set_attributes_from_name('group')
    ScheduleEntry._meta.add_field(field)


def reverse_add_group_field_state(apps, schema_editor):
    """Обратная операция - удаляем поле из состояния"""
    ScheduleEntry = apps.get_model('main', 'ScheduleEntry')
    ScheduleEntry._meta.remove_field('group')


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_rename_main_attend_date_idx_main_attend_date_afda52_idx_and_more"),
    ]

    operations = [
        # Операции с базой данных - проверяем и добавляем поле только если его нет
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
        # Обновляем состояние Django через RunPython (не выполняет SQL)
        migrations.RunPython(
            add_group_field_state,
            reverse_add_group_field_state,
        ),
    ]



