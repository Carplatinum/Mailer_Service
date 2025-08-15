from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.timezone import now
from django.db import transaction

from mailing.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = ('Отправляет все активные рассылки '
            'со статусом "running" и логирует попытки отправки')

    def handle(self, *args, **options):
        # Получаем все рассылки, у которых статус 'running'
        # и которые еще не завершены по времени
        mailings = Mailing.objects.filter(status='running', last_send__gte=now())

        if not mailings.exists():
            self.stdout.write('Нет активных рассылок для отправки.')
            return

        for mailing in mailings:
            self.stdout.write(f'Обрабатываем рассылку ID={mailing.id}, '
                              f'сообщение: "{mailing.message.subject}"')

            # Для каждого получателя будем отправлять письмо
            recipients = mailing.recipients.all()
            if not recipients.exists():
                self.stdout.write(' - Нет получателей, пропускаем.')
                continue

            sent_count = 0
            failed_count = 0

            for recipient in recipients:
                try:
                    with transaction.atomic():
                        send_mail(
                            subject=mailing.message.subject,
                            message=mailing.message.body,
                            from_email=None,
                            recipient_list=[recipient.email],
                            fail_silently=False,
                        )

                        MailingAttempt.objects.create(
                            mailing=mailing,
                            status='success',
                            mail_server_response='OK',
                        )
                        sent_count += 1
                        self.stdout.write(f'  - Письмо '
                                          f'успешно отправлено {recipient.email}')

                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status='fail',
                        mail_server_response=str(e),
                    )
                    failed_count += 1
                    self.stdout.write(f'  - Ошибка отправки '
                                      f'{recipient.email}: {str(e)}')

            # Обновляем дату последней отправки рассылки
            mailing.last_send = now()

            # Если срок рассылки истёк — меняем статус на 'finished'
            if mailing.last_send > mailing.last_send:
                mailing.status = 'finished'
                self.stdout.write(' - Рассылка помечена как завершенная.')

            mailing.save()

            self.stdout.write(
                f'Рассылка ID={mailing.id}: '
                f'успешно отправлено {sent_count}, неудачно {failed_count}'
            )
        self.stdout.write(self.style.SUCCESS('Отправка рассылок завершена.'))
