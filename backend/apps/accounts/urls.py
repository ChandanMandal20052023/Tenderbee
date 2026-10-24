"""
URL endpoints for Authentication & Accounts.
"""
from django.urls import path
from apps.accounts.views import (
    CurrentUserAPIView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    RegisterAPIView,
)

app_name = "accounts"

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", CustomTokenVerifyView.as_view(), name="token-verify"),
    path("register/", RegisterAPIView.as_view(), name="auth-register"),
    path("me/", CurrentUserAPIView.as_view(), name="auth-me"),
]
