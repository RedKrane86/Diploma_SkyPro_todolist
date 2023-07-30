from abc import ABCMeta

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, exceptions

from core.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_repeat = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_repeat']:
            raise exceptions.ValidationError('Password not match')
        return attrs

    def create(self, validated_data: dict) -> User:
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, validators=[validate_password])
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, old_password: str) -> str:
        request = self.context['request']

        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated

        if not request.user.check_password(old_password):
            raise exceptions.ValidationError('Password not correct')

        return old_password
