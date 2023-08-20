from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, exceptions

from core.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания пользователя
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_repeat = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs: dict) -> dict:
        """
        Валидация полей 'password' и 'password_repeat'.
        При не совпадении создает ошибку
        """
        if attrs['password'] != attrs['password_repeat']:
            raise exceptions.ValidationError('Password not match')
        return attrs

    def create(self, validated_data: dict) -> User:
        """
        Запись пароля на основе провалидированных данных.
        Для устранения ошибок, поле validated_data удаляется
        """
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для логина пользователя
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UpdatePasswordSerializer(serializers.Serializer):
    """
    Сериализатор обновления пароля
    """
    old_password = serializers.CharField(required=True, validators=[validate_password])
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, old_password: str) -> str:
        """
        Валидация старого и нового паролей
        Выдать ошибку если:
            - Пользователь не аутентифицирован
            - Пользователь неправильно ввел пароль в поле 'old_password'
        """
        request = self.context['request']

        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated

        if not request.user.check_password(old_password):
            raise exceptions.ValidationError('Password not correct')

        return old_password
