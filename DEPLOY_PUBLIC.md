# 🚀 Публичный доступ к UniQuest

Инструкции по развертыванию сайта для публичного доступа без использования платформ типа Render.

## 📋 Варианты развертывания

### 1. Быстрый доступ через ngrok (рекомендуется для тестирования)

ngrok создает безопасный туннель к вашему локальному серверу.

#### Установка ngrok:
1. Скачайте ngrok с https://ngrok.com/download
2. Зарегистрируйтесь и получите бесплатный токен
3. Распакуйте и добавьте в PATH

#### Использование:
```bash
# 1. Запустите Django сервер локально
python manage.py runserver

# 2. В другом терминале запустите ngrok
ngrok http 8000

# 3. Скопируйте URL вида: https://xxxx-xx-xx-xxx-xx.ngrok.io
# Этот URL будет работать из любого места в интернете!
```

### 2. Доступ из локальной сети

Для доступа с других устройств в вашей сети:

```bash
# Используйте скрипт для автоматического запуска
python start_public_server.py

# Или вручную:
python manage.py runserver 0.0.0.0:8000
```

Затем откройте на другом устройстве: `http://ВАШ-IP:8000`

### 3. Развертывание на VPS/сервере

#### Требования:
- Ubuntu/Debian сервер
- Python 3.9+
- PostgreSQL
- Доступ по SSH

#### Шаги:

1. **Подключитесь к серверу:**
```bash
ssh user@your-server-ip
```

2. **Установите зависимости:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx git
```

3. **Клонируйте проект:**
```bash
git clone https://github.com/yourusername/uniquest.git
cd uniquest
```

4. **Создайте виртуальное окружение:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Настройте базу данных PostgreSQL:**
```bash
sudo -u postgres psql
CREATE DATABASE uniquestus;
CREATE USER uniquest_user WITH PASSWORD 'your_secure_password';
ALTER ROLE uniquest_user SET client_encoding TO 'utf8';
ALTER ROLE uniquest_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE uniquest_user SET timezone TO 'Asia/Almaty';
GRANT ALL PRIVILEGES ON DATABASE uniquestus TO uniquest_user;
\q
```

6. **Настройте переменные окружения:**
```bash
nano .env
```

Добавьте:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
DB_NAME=uniquestus
DB_USER=uniquest_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=your-domain.com,your-server-ip
```

7. **Обновите settings.py для использования .env:**
```python
# Добавьте в начало settings.py
from dotenv import load_dotenv
load_dotenv()
```

8. **Примените миграции:**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

9. **Создайте суперпользователя:**
```bash
python manage.py createsuperuser
```

10. **Настройте Gunicorn:**
```bash
pip install gunicorn
```

Создайте файл `gunicorn_config.py`:
```python
bind = "127.0.0.1:8000"
workers = 3
timeout = 120
```

11. **Создайте systemd service:**
```bash
sudo nano /etc/systemd/system/uniquest.service
```

Добавьте:
```ini
[Unit]
Description=UniQuest Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/uniquest
ExecStart=/path/to/uniquest/venv/bin/gunicorn \
    --config /path/to/uniquest/gunicorn_config.py \
    uniquest.wsgi:application

[Install]
WantedBy=multi-user.target
```

Активируйте:
```bash
sudo systemctl daemon-reload
sudo systemctl enable uniquest
sudo systemctl start uniquest
```

12. **Настройте Nginx:**
```bash
sudo nano /etc/nginx/sites-available/uniquest
```

Добавьте:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/uniquest/staticfiles/;
    }

    location /media/ {
        alias /path/to/uniquest/media/;
    }
}
```

Активируйте:
```bash
sudo ln -s /etc/nginx/sites-available/uniquest /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

13. **Настройте SSL (Let's Encrypt):**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 4. Использование Cloudflare Tunnel (бесплатно)

Cloudflare Tunnel не требует открытых портов и работает из любого места.

1. Зарегистрируйтесь на https://cloudflare.com
2. Добавьте ваш домен
3. Установите cloudflared:
```bash
# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Windows
# Скачайте с https://github.com/cloudflare/cloudflared/releases
```

4. Создайте туннель:
```bash
cloudflared tunnel login
cloudflared tunnel create uniquest
```

5. Настройте маршрут:
```bash
cloudflared tunnel route dns uniquest your-subdomain.your-domain.com
```

6. Создайте config.yml:
```yaml
tunnel: uniquest-id
credentials-file: /path/to/credentials.json

ingress:
  - hostname: your-subdomain.your-domain.com
    service: http://localhost:8000
  - service: http_status:404
```

7. Запустите туннель:
```bash
cloudflared tunnel --config config.yml run uniquest
```

## 🔒 Безопасность

### Для production обязательно:

1. **Измените SECRET_KEY:**
```python
# В settings.py или .env
SECRET_KEY = 'your-very-long-random-secret-key'
```

2. **Отключите DEBUG:**
```python
DEBUG = False
```

3. **Укажите конкретные хосты:**
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

4. **Используйте HTTPS** (через Let's Encrypt)

5. **Настройте файрвол:**
```bash
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

## 📝 Быстрый старт (ngrok)

Самый простой способ для быстрого тестирования:

```bash
# 1. Установите ngrok
# 2. Запустите Django
python manage.py runserver

# 3. В другом терминале
ngrok http 8000

# 4. Используйте предоставленный URL!
```

## 🆘 Решение проблем

### Порт уже занят:
```bash
# Используйте другой порт
python manage.py runserver 0.0.0.0:8080
```

### Не могу подключиться из сети:
- Проверьте файрвол Windows/Linux
- Убедитесь, что сервер запущен на 0.0.0.0 (не 127.0.0.1)
- Проверьте настройки роутера

### Статика не загружается:
```bash
python manage.py collectstatic --noinput
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи Django
2. Проверьте логи nginx/gunicorn
3. Убедитесь, что все порты открыты
4. Проверьте настройки ALLOWED_HOSTS

