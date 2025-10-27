from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = (
            "id", "phone", "address", "city", "postal_code", 
            "date_of_birth", "avatar", "full_name", "created_at", "updated_at"
        )
        read_only_fields = ("created_at", "updated_at")


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name", 
            "is_active", "date_joined", "profile"
        )
        read_only_fields = ("id", "date_joined", "is_active")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "password", "password_confirm")

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # Создаем профиль для нового пользователя
        Profile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)





