from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('email', 'username', 'phone', 'country', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Персональная информация', {'fields': ('phone', 'country', 'avatar')}),
        ('Права и группы', {'fields': ('is_staff',
                                       'is_active', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone', 'country',
                       'avatar', 'password1', 'password2', 'is_staff',
                       'is_active', 'groups', 'user_permissions'),
        }),
    )
    search_fields = ('email', 'username', 'phone', 'country')
    ordering = ('email',)
