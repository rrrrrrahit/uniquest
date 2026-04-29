from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed_render_test_accounts(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Profile = apps.get_model("main", "Profile")

    accounts = [
        {
            "username": "kamila.zholdaskyzy",
            "first_name": "Камила",
            "last_name": "Жолдаскызы",
            "email": "kamila.zholdaskyzy@student.uniquest.kz",
            "password": "Kamila2026!",
            "role": "student",
            "is_staff": False,
        },
        {
            "username": "a.lebedev",
            "first_name": "Андрей",
            "last_name": "Лебедев",
            "email": "a.lebedev@uniquest.kz",
            "password": "Lebedev2026!",
            "role": "teacher",
            "is_staff": True,
        },
        {
            "username": "lebedev",
            "first_name": "Андрей",
            "last_name": "Лебедев",
            "email": "lebedev@uniquest.kz",
            "password": "Lebedev2026!",
            "role": "teacher",
            "is_staff": True,
        },
    ]

    for row in accounts:
        user, _ = User.objects.update_or_create(
            username=row["username"],
            defaults={
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "is_active": True,
                "is_staff": row["is_staff"],
                "password": make_password(row["password"]),
            },
        )

        profile, _ = Profile.objects.get_or_create(user_id=user.id)
        profile.role = row["role"]
        if row["role"] == "teacher":
            profile.group_id = None
            profile.specialty_id = None
        profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0010_remove_scheduleentry_group"),
    ]

    operations = [
        migrations.RunPython(seed_render_test_accounts, migrations.RunPython.noop),
    ]

