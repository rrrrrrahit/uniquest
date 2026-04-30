from django.db import migrations, models


def _infer_course_year(group_name: str) -> int:
    # IT-101 -> 1, IT-201 -> 2, ECO-301 -> 3, etc.
    if not group_name:
        return 1
    parts = group_name.split("-")
    if len(parts) < 2:
        return 1
    suffix = parts[1].strip()
    if not suffix:
        return 1
    first = suffix[0]
    if first.isdigit():
        value = int(first)
        if 1 <= value <= 4:
            return value
    return 1


def backfill_course_year(apps, schema_editor):
    Group = apps.get_model("main", "Group")
    for group in Group.objects.all():
        group.course_year = _infer_course_year(getattr(group, "name", ""))
        group.save(update_fields=["course_year"])


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0013_expand_render_demo_academics"),
    ]

    operations = [
        migrations.AddField(
            model_name="group",
            name="course_year",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "1 курс"), (2, "2 курс"), (3, "3 курс"), (4, "4 курс")],
                default=1,
                verbose_name="Курс обучения",
            ),
        ),
        migrations.RunPython(backfill_course_year, migrations.RunPython.noop),
    ]

