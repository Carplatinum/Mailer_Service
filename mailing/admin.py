from django.contrib import admin
from .models import Mailing, Message, Recipient, MailingAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'owner')
    search_fields = ('full_name', 'email')
    list_filter = ('owner',)
    readonly_fields = ()  # по необходимости


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner')
    search_fields = ('subject', 'body')
    list_filter = ('owner',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'status',
        'start_time',
        'end_time',
        'owner',
        'message_display',
    )
    list_filter = ('status', 'owner')
    search_fields = ('message__subject',)
    filter_horizontal = ('recipients',)  # удобный вид отбора many-to-many
    readonly_fields = ('start_time', 'end_time')

    def message_display(self, obj):
        return obj.message.subject

    message_display.short_description = 'Сообщение'


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'attempt_time', 'status')
    list_filter = ('status', 'mailing')
    search_fields = ('server_response',)
