from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views


app_name = "account"

urlpatterns = [
    path('list/', views.UserListView.as_view(), name='list'),
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', views.ActivateAccount.as_view(), name='activate'),
    path('password_change/', views.ChangePasswordView.as_view(), name='password_change'),
    path('password_reset/', views.ResetPasswordView.as_view(), name='password_reset'),
    path('password_reset/<uidb64>/<token>/', views.PasswordResetCheckTokenView.as_view(), name='password_reset_check_token'),
    path('password_reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm')
]
