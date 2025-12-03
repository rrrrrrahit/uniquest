from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Создает администратора для входа в админку'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin123456'
        email = 'admin@uniquest.kz'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS('✅ Администратор создан успешно!'))
        else:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS('✅ Пароль администратора обновлен!'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Данные для входа в админку:'))
        self.stdout.write(self.style.SUCCESS(f'Логин: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Пароль: {password}'))
        self.stdout.write(self.style.SUCCESS('='*50))

