from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'country', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем bootstrap классы для админки (если нужно)
        for field_name, field in self.fields.items():
            css_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css_class + ' form-control').strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'country', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем bootstrap классы для админки (если нужно)
        for field_name, field in self.fields.items():
            if field_name == 'password':
                continue  # Не стилизуем поле пароля
            css_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css_class + ' form-control').strip()
