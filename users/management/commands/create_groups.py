from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from mailing.models import Mailing, Recipient, Message


class Command(BaseCommand):
    help = (
        'Создает группу "Managers" с правами '
        'на просмотр рассылок, сообщений и получателей'
    )

    def handle(self, *args, **options):
        group_name = 'Managers'
        managers_group, created = Group.objects.get_or_create(name=group_name)

        # Список моделей, к которым нужно дать права просмотра для менеджеров
        models = [Mailing, Recipient, Message]

        permissions = []
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            # Получаем права на просмотр (view) модели
            view_permission = Permission.objects.filter(
                content_type=content_type,
                codename__startswith='view_'
            )
            permissions.extend(view_permission)

        # Назначаем все найденные права группе
        managers_group.permissions.set(permissions)
        managers_group.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Группа "{group_name}" успешно создана '
                    f'с правами просмотра моделей.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Группа "{group_name}" уже существует, права обновлены.'
                )
            )
