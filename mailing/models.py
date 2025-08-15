from django.db import models
from django.conf import settings


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipients'
    )

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылок"
        permissions = [
            ('view_all_recipients', 'Can view all recipients (managers)'),
            # Можно добавить другие права по необходимости
        ]


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ('view_all_messages', 'Can view all messages (managers)'),
        ]


class Mailing(models.Model):
    STATUS_CREATED = 'created'
    STATUS_STARTED = 'started'
    STATUS_FINISHED = 'finished'

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_STARTED, 'Запущена'),
        (STATUS_FINISHED, 'Завершена'),
    ]

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings'
    )
    recipients = models.ManyToManyField(
        Recipient,
        related_name='mailings',
        blank=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings'
    )

    def __str__(self):
        return f"Рассылка #{self.pk} - {self.status}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ('view_all_mailings', 'Can view all mailings (managers)'),
            ('manage_mailings', 'Can manage mailings'),
        ]


class MailingAttempt(models.Model):
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAILED, 'Не успешно'),
    ]

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=7,
        choices=STATUS_CHOICES
    )
    server_response = models.TextField(blank=True)

    def __str__(self):
        return (f"Попытка рассылки {self.mailing_id} "
                f"в {self.attempt_time} - {self.status}")

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
