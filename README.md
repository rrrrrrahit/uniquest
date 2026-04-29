# UniQuest - Образовательная платформа Казахстана

Современная платформа для управления обучением студентов и преподавателей с функциями ИИ/ML.

## 🚀 Быстрый старт

### Для локальной разработки:

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Примените миграции
python manage.py migrate

# 3. Заполните демо-данные (реалистичные группы, студенты, курсы, лекции)
python manage.py seed_demo --students 500 --groups 20 --courses 30 --seed 42

# 4. Обучите модель прогноза итоговой оценки
python manage.py train_grade_model --save-path=models/grade_model.pkl

# 5. Проиндексируйте лекции для семантического поиска
python manage.py index_lectures

# 6. Запустите сервер (общий доступ в локальной сети)
python manage.py runserver
```

После запуска сайт будет доступен:
- локально: `http://127.0.0.1:8000/`
- в вашей локальной сети: `http://<ваш-ip>:8000/`

### Развёртывание на Render

В настройках сервиса укажите:

- **Build Command:**  
  `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start Command:**  
  `python manage.py migrate --noinput && gunicorn uniquest.wsgi:application --bind 0.0.0.0:$PORT`

Для публичного домена (например, `uniquest.kz`) добавьте переменные окружения:

- `ALLOWED_HOSTS=.onrender.com,uniquest.kz,www.uniquest.kz`
- `CSRF_TRUSTED_ORIGINS=https://*.onrender.com,https://uniquest.kz,https://www.uniquest.kz`

После первого запуска выполните в Render Shell:

```bash
python manage.py seed_demo --students 500 --groups 20 --courses 30 --seed 42
python manage.py train_grade_model --save-path=models/grade_model.pkl
python manage.py index_lectures
```

## 👥 Демо‑аккаунты

Справочник с логинами и паролями находится в `DEMO_ACCOUNTS.md` (например, студент `suraya` / `Suraya2025!`, преподаватель `m.zhasuzakova` / `Teacher2025!`).

## 📚 Документация

- **Основные команды и эндпоинты:** этот файл (`README.md`)
- **Учётные записи:** `DEMO_ACCOUNTS.md`
- **Настройки окружения:** `env.example`

## ✨ Особенности

- ✅ Профессиональный деловой дизайн
- ✅ Раздельный доступ для студентов и преподавателей
- ✅ Преподаватель может добавлять оценки и учебные ресурсы прямо из панели
- ✅ ИИ/ML анализ успеваемости и прогноз итоговой оценки
- ✅ Семантический поиск по лекциям и материалам (embeddings + BM25)
- ✅ Казахстанский контекст (специальности, предметы, имена студентов)
- ✅ Готовые реальные данные (Айдинова С. Р., Жасұзақова М. Ж., расписание, оценки)
- ✅ Готов к развертыванию на облаке

## 🛠️ Технологии

- Django 5.2
- PostgreSQL
- Bootstrap 5
- Python ML библиотеки (scikit-learn, numpy, pandas)
- WhiteNoise для статики

## 📝 Лицензия

Проект создан для образовательных целей.
https://docs.google.com/spreadsheets/d/1oDHMUbaw5qu1WphTrwLt3dWd9EHTW4RYWdAeFOZxhhg/edit?pli=1&gid=0#gid=0
