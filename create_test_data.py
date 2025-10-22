from main.models import Course
from django.contrib.auth.models import User

# Создаем тестового преподавателя
teacher, created = User.objects.get_or_create(
    username='teacher1',
    defaults={
        'email': 'teacher@uniquest.com',
        'first_name': 'Anna',
        'last_name': 'Petrova'
    }
)
if created:
    teacher.set_password('password123')
    teacher.save()
    print('Created teacher:', teacher.username)

# Создаем тестовые курсы
courses_data = [
    {
        'title': 'Programming Basics',
        'code': 'CS101',
        'description': 'Learn basic programming concepts in Python. Includes variables, loops, functions and OOP basics.',
        'teacher': teacher
    },
    {
        'title': 'Web Development',
        'code': 'WEB201',
        'description': 'Create modern web applications using HTML, CSS, JavaScript and Django.',
        'teacher': teacher
    },
    {
        'title': 'Database Design',
        'code': 'DB301',
        'description': 'Design and manage relational databases. SQL, normalization, indexes.',
        'teacher': teacher
    },
    {
        'title': 'Algorithms and Data Structures',
        'code': 'ALG401',
        'description': 'Study basic sorting, searching algorithms and data structures for efficient programming.',
        'teacher': teacher
    },
    {
        'title': 'Machine Learning',
        'code': 'ML501',
        'description': 'Introduction to machine learning: classification, regression, neural networks and deep learning.',
        'teacher': teacher
    },
    {
        'title': 'Cybersecurity',
        'code': 'SEC601',
        'description': 'Basics of information security: cryptography, attack protection, ethical hacking.',
        'teacher': teacher
    }
]

for course_data in courses_data:
    course, created = Course.objects.get_or_create(
        code=course_data['code'],
        defaults=course_data
    )
    if created:
        print(f'Created course: {course.title}')
    else:
        print(f'Course already exists: {course.title}')

print('Test data created successfully!')
