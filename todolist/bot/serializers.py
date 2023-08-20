from rest_framework import serializers

from bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя телеграмм
    """
    class Meta:
        model = TgUser
        fields = ('verification_code',)

