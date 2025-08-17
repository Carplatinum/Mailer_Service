from django.urls import path
from .views import (
    UserRegisterView, UserLoginView, UserLogoutView,
    UserPasswordResetView, UserPasswordResetDoneView,
    UserPasswordResetConfirmView, UserPasswordResetCompleteView,
    profile_view, profile_update_view,
)

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path('password_reset/', UserPasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/', UserPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', UserPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    path('profile/', profile_view, name='profile'),
    path('profile/update/', profile_update_view, name='profile_update'),
]
