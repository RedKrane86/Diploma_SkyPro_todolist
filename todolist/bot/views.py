from typing import Any

from rest_framework import generics, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient


class VerificationCodeView(generics.UpdateAPIView):
    """
    Представление для верификации пользователя телеграмм
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TgUserSerializer
    queryset = TgUser.objects.all()

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Отправляет код верификации.
        Если пользователя не существует, выдает ошибку
        """
        try:
            tg_user = self.get_queryset().get(verification_code=request.data.get('verification_code'))
        except TgUser.DoesNotExist:
            raise AuthenticationFailed

        tg_user.user = request.user
        tg_user.save()
        TgClient().send_message(chat_id=tg_user.chat_id, text='Бот верифицирован')
        return Response(TgUserSerializer(tg_user).data)
