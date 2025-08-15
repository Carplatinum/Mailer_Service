from django.urls import path
from .views import (
    RecipientListView, RecipientCreateView, RecipientUpdateView, RecipientDeleteView,
    MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView,
    MailingListView, MailingCreateView, MailingUpdateView, MailingDeleteView,
    MailingDetailView, send_mailing, MailingAttemptListView,
)

app_name = 'mailing'

urlpatterns = [
    # Получатели рассылки
    path('recipients/', RecipientListView.as_view(), name='recipient_list'),
    path('recipients/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/update/',
         RecipientUpdateView.as_view(),
         name='recipient_update'),
    path('recipients/<int:pk>/delete/',
         RecipientDeleteView.as_view(), name='recipient_delete'),

    # Сообщения
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/',
         MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/',
         MessageDeleteView.as_view(), name='message_delete'),

    # Рассылки
    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/<int:pk>/update/',
         MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/',
         MailingDeleteView.as_view(),
         name='mailing_delete'),

    # Отправка рассылки вручную (POST)
    path('mailings/send/<int:pk>/', send_mailing, name='send_mailing'),

    # Попытки рассылок
    path('mailing_attempts/',
         MailingAttemptListView.as_view(),
         name='mailing_attempt_list'),
]
