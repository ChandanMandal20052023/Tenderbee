"""
Authentication & Organization Views for TenderBee.
Includes JWT token generation, refresh, verification, and registration.
"""
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.accounts.serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    POST /api/v1/auth/token/
    Takes user email/password and returns JWT access + refresh tokens with tenant claims.
    """
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """
    POST /api/v1/auth/token/refresh/
    Refreshes an expired access token using a valid refresh token.
    """
    permission_classes = (AllowAny,)


class CustomTokenVerifyView(TokenVerifyView):
    """
    POST /api/v1/auth/token/verify/
    Verifies that a JWT token is valid and unexpired.
    """
    permission_classes = (AllowAny,)


class RegisterAPIView(APIView):
    """
    POST /api/v1/auth/register/
    Registers a new tenant Organization and creates the primary Admin user.
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        profile_data = UserProfileSerializer(user).data
        return Response(
            {
                "success": True,
                "message": "Tenant organization and administrator user registered successfully.",
                "user": profile_data,
            },
            status=status.HTTP_201_CREATED,
        )


class CurrentUserAPIView(APIView):
    """
    GET /api/v1/auth/me/
    Returns authenticated user information and organization details.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
