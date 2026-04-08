from django.db import migrations, models
import django.db.models.deletion


def add_scheduleentry_group_column(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='main_scheduleentry' AND column_name='group_id'
                ) THEN
                    ALTER TABLE main_scheduleentry
                    ADD COLUMN group_id INTEGER NULL
                    REFERENCES main_group(id) ON DELETE SET NULL;
                END IF;
            END $$;
            """
        )
        return

    # SQLite/local: добавляем колонку только если ее нет.
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(main_scheduleentry)")
        columns = [row[1] for row in cursor.fetchall()]
    if "group_id" not in columns:
        schema_editor.execute("ALTER TABLE main_scheduleentry ADD COLUMN group_id INTEGER NULL")


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_rename_main_attend_date_idx_main_attend_date_afda52_idx_and_more"),
    ]

    operations = [
        # Используем SeparateDatabaseAndState для правильного управления состоянием
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_scheduleentry_group_column, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='scheduleentry',
                    name='group',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='schedule_entries',
                        to='main.group',
                        verbose_name='Учебная группа',
                    ),
                ),
            ],
        ),
    ]



