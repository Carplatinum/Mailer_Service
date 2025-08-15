import logging
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from .models import Mailing, Message, Recipient, MailingAttempt
from .forms import MailingForm, MessageForm, RecipientForm


MANAGER_GROUP_NAME = 'Менеджеры'
logger = logging.getLogger(__name__)


class OwnerMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        if user.groups.filter(name=MANAGER_GROUP_NAME).exists():
            return True
        return obj.owner == user

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет доступа к этому объекту.")
        return redirect('mailing:mailing_list')


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    context_object_name = 'mailings'
    template_name = 'mailing/mailing_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name=MANAGER_GROUP_NAME).exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


class MailingDetailView(LoginRequiredMixin, OwnerMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_create.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_update.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs


class MailingDeleteView(LoginRequiredMixin, OwnerMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    context_object_name = 'messages'
    template_name = 'mailing/message_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name=MANAGER_GROUP_NAME).exists():
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_create.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_update.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageDeleteView(LoginRequiredMixin, OwnerMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_delete.html'
    success_url = reverse_lazy('mailing:message_list')


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    context_object_name = 'recipients'
    template_name = 'mailing/recipient_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name=MANAGER_GROUP_NAME).exists():
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_create.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, OwnerMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_update.html'
    success_url = reverse_lazy('mailing:recipient_list')


class RecipientDeleteView(LoginRequiredMixin, OwnerMixin, DeleteView):
    model = Recipient
    template_name = 'mailing/recipient_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    context_object_name = 'attempts'
    template_name = 'mailing/mailing_attempt_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name=MANAGER_GROUP_NAME).exists():
            return MailingAttempt.objects.all().select_related('mailing')
        return MailingAttempt.objects.filter(
            mailing__owner=user
        ).select_related('mailing')


@require_POST
@login_required
def send_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    user = request.user

    if mailing.owner != user:
        messages.error(request, "У вас нет прав для запуска этой рассылки.")
        return redirect('mailing:mailing_list')

    recipients = mailing.recipients.all()
    message = mailing.message

    success_count = 0
    fail_count = 0

    for recipient in recipients:
        try:
            send_mail(
                subject=message.subject,
                message=message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                mailing=mailing,
                status='success',
                server_response='Отправлено успешно',
            )
            success_count += 1
        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status='failed',
                server_response=str(e),
            )
            logger.error(
                f"Ошибка отправки письма "
                f"получателю {recipient.email}: {e}",
                exc_info=True,
            )
            fail_count += 1

    now = timezone.now()
    if mailing.status == Mailing.STATUS_CREATED:
        mailing.status = Mailing.STATUS_STARTED
        if not mailing.start_time:
            mailing.start_time = now
    mailing.end_time = now
    mailing.save()

    messages.success(
        request,
        f"Рассылка выполнена: успешно - {success_count}, неуспешно - {fail_count}",
    )
    return redirect('mailing:mailing_list')
