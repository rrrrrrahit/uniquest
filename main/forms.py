from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Specialty, Grade, Enrollment, Course, Lecture, Group

# ----------------- Регистрация пользователя -----------------
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=False, label='Имя')
    last_name = forms.CharField(required=False, label='Фамилия')
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True, label='Роль')
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='Группа',
        help_text='Учебная группа (для студентов)'
    )
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
        label='Специальность',
        help_text='Выберите специальность (для студентов)'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = Group.objects.all().order_by('-year', 'name')
        self.fields['specialty'].queryset = Specialty.objects.all().order_by('code', 'name_ru')
        self.fields['group'].empty_label = '---------'
        self.fields['specialty'].empty_label = '---------'

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'group', 'specialty', 'password1', 'password2']
        labels = {'username': 'Логин'}

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        group = cleaned_data.get('group')
        specialty = cleaned_data.get('specialty')

        if role == Profile.ROLE_STUDENT:
            if not Group.objects.exists():
                self.add_error('group', 'В системе пока нет учебных групп. Обратитесь к администратору.')
            if not Specialty.objects.exists():
                self.add_error('specialty', 'В системе пока нет специальностей. Обратитесь к администратору.')
            if not group:
                self.add_error('group', 'Для студента необходимо указать учебную группу.')
            if not specialty:
                self.add_error('specialty', 'Для студента необходимо указать специальность.')
        elif role == Profile.ROLE_TEACHER:
            # For teachers, these fields must stay empty.
            cleaned_data['group'] = None
            cleaned_data['specialty'] = None

        return cleaned_data

# ----------------- Обновление пользователя -----------------
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
        }

# ----------------- Обновление профиля -----------------
class ProfileUpdateForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        role = None
        if user and hasattr(user, 'profile'):
            role = user.profile.role

        # Student-specific fields are hidden for teachers.
        if role == Profile.ROLE_TEACHER:
            self.fields.pop('group', None)
            self.fields.pop('specialty', None)

    def save(self, commit=True):
        profile = super().save(commit=False)
        role = getattr(profile, 'role', None)
        if role == Profile.ROLE_TEACHER:
            profile.group = None
            profile.specialty = None
        if commit:
            profile.save()
        return profile

    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'phone', 'group', 'specialty', 'address', 'iin']
        widgets = {
            'bio': forms.Textarea(attrs={'rows':3, 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows':2, 'class': 'form-control'}),
            'iin': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'photo': 'Фото',
            'bio': 'Биография',
            'phone': 'Телефон',
            'group': 'Группа',
            'specialty': 'Специальность',
            'address': 'Адрес',
            'iin': 'ИИН',
        }

# ----------------- Форма выставления оценки преподавателем -----------------
class TeacherGradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['enrollment', 'assignment', 'value', 'topic', 'comment']
        labels = {
            'enrollment': 'Студент и курс',
            'assignment': 'Задание',
            'value': 'Балл',
            'topic': 'Тема',
            'comment': 'Комментарий',
        }
        widgets = {'comment': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher = teacher
        qs = Enrollment.objects.select_related('student__user', 'course')
        if teacher:
            qs = qs.filter(course__teacher=teacher)
        self.fields['enrollment'].queryset = qs
        self.fields['enrollment'].label_from_instance = lambda enr: f"{enr.student.last_name} {enr.student.first_name} — {enr.course.name}"

    def clean_enrollment(self):
        enrollment = self.cleaned_data.get('enrollment')
        if self.teacher and enrollment.course.teacher != self.teacher:
            raise forms.ValidationError('Можно выбирать только собственных студентов.')
        return enrollment

# ----------------- Создание лекции/ресурса -----------------
class LectureCreateForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['course', 'title', 'content_text', 'content_url']
        labels = {
            'course': 'Курс',
            'title': 'Название лекции/ресурса',
            'content_text': 'Содержание',
            'content_url': 'Ссылка (необязательно)',
        }
        widgets = {'content_text': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Course.objects.all()
        if teacher:
            qs = qs.filter(teacher=teacher)
        self.fields['course'].queryset = qs
