"""
Скрипт для запуска Django сервера с публичным доступом
"""
import os
import sys
import socket

def get_local_ip():
    """Получает локальный IP адрес для доступа из сети"""
    try:
        # Подключаемся к внешнему серверу чтобы узнать наш IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    # Устанавливаем переменные окружения
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uniquest.settings')
    
    # Получаем IP адрес
    local_ip = get_local_ip()
    port = os.environ.get('PORT', '8000')
    
    print("=" * 60)
    print("🚀 ЗАПУСК PUBLIС СЕРВЕРА UNIQUEST")
    print("=" * 60)
    print(f"\n📍 Локальный доступ:")
    print(f"   http://127.0.0.1:{port}")
    print(f"\n🌐 Доступ из вашей сети:")
    print(f"   http://{local_ip}:{port}")
    print(f"\n⚠️  ВНИМАНИЕ:")
    print(f"   - Убедитесь, что порт {port} открыт в файрволе")
    print(f"   - Для доступа из интернета используйте ngrok (см. инструкции)")
    print(f"   - В production используйте gunicorn + nginx")
    print("=" * 60)
    print("\nНажмите Ctrl+C для остановки сервера\n")
    
    # Импортируем Django
    import django
    from django.core.management import execute_from_command_line
    from django.core.management.commands.runserver import Command as RunserverCommand
    
    django.setup()
    
    # Запускаем сервер на всех интерфейсах (0.0.0.0)
    execute_from_command_line([
        'manage.py',
        'runserver',
        f'0.0.0.0:{port}',  # 0.0.0.0 позволяет доступ из сети
        '--noreload'  # Отключаем автоперезагрузку для стабильности
    ])

