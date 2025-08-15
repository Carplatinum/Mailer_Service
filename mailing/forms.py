
from django import forms
from .models import Mailing, Message, Recipient


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email получателя'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ф.И.О.'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Комментарий'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if Recipient.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "Пользователь с таким email уже существует."
                )
        return email


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема письма'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Текст письма'
            }),
        }

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if subject and len(subject) > 255:
            raise forms.ValidationError(
                "Длина темы не должна превышать 255 символов."
            )
        return subject


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = [
            'start_time',
            'end_time',
            'status',
            'message',
            'recipients',
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Select(attrs={'class': 'form-select'}),
            'recipients': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 10
            }),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if current_user:
            self.fields['recipients'].queryset = Recipient.objects.filter(
                owner=current_user
            )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time > end_time:
            raise forms.ValidationError(
                "Дата и время начала рассылки должны быть меньше "
                "или равны дате и времени окончания."
            )

        return cleaned_data
