from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Specialty

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=False, label='Имя')
    last_name = forms.CharField(required=False, label='Фамилия')
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True, label='Роль')
    group = forms.CharField(required=False, label='Группа', help_text='Учебная группа (для студентов)')
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
        label='Специальность',
        help_text='Выберите специальность (для студентов)'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'group', 'specialty', 'password1', 'password2']
        labels = {
            'username': 'Логин',
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'phone', 'group', 'specialty', 'address', 'iin']
        widgets = {
            'bio': forms.Textarea(attrs={'rows':3, 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'group': forms.TextInput(attrs={'class': 'form-control'}),
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
