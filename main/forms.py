from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)
    group = forms.CharField(required=False, help_text='Учебная группа (для студентов)')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'group', 'password1', 'password2']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'phone', 'group']
        widgets = {
            'bio': forms.Textarea(attrs={'rows':3})
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
