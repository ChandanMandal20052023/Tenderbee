"""
Serializers for User authentication, Registration, and JWT Token with tenant claims.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.accounts.models import Organization, UserRole

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "gstin", "udyam_number", "pan", "created_at")
        read_only_fields = ("id", "created_at")


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT Token Serializer that injects tenant context into claims.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Custom claims embedded into JWT token payload
        token["email"] = user.email
        token["role"] = user.role
        token["org_id"] = user.organization.id if user.organization else "org_default"
        token["org_name"] = user.organization.name if user.organization else "Default Tenant"
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add profile info directly into the login response
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "username": self.user.username,
            "role": self.user.role,
            "organization": OrganizationSerializer(self.user.organization).data if self.user.organization else None,
        }
        return data


class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for creating a new Organization tenant along with the initial Admin user.
    """
    organization_name = serializers.CharField(max_length=255, required=True)
    gstin = serializers.CharField(max_length=15, required=False, allow_blank=True)
    udyam_number = serializers.CharField(max_length=30, required=False, allow_blank=True)
    pan = serializers.CharField(max_length=10, required=False, allow_blank=True)

    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        org_name = validated_data.pop("organization_name")
        gstin = validated_data.get("gstin", "")
        udyam = validated_data.get("udyam_number", "")
        pan = validated_data.get("pan", "")

        email = validated_data["email"]
        username = validated_data.get("username") or email.split("@")[0]
        password = validated_data["password"]

        with transaction.atomic():
            org = Organization.objects.create(
                name=org_name,
                gstin=gstin,
                udyam_number=udyam,
                pan=pan,
            )
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                organization=org,
                role=UserRole.ADMIN,
            )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "username", "role", "organization", "date_joined")
        read_only_fields = fields
