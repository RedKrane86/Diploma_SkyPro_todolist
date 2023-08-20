import logging
from typing import TypeVar, Type

import requests
from django.conf import settings
from pydantic import ValidationError
from pydantic.main import BaseModel

from bot.tg.schemas import GetUpdatesResponse, SendMessageResponse

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class TgClient:
    """
    Класс взаимодействия с api.telegram.org/bot
    """
    def __init__(self, token: str | None = None):
        self.__token = token if token else settings.BOT_TOKEN
        self.__url = f'https://api.telegram.org/bot{self.__token}/'

    def __get_url(self, method: str) -> str:
        """
        Автоматически подставляет под url команду
        """
        return f'{self.__url}{method}'

    def get_updates(self, offset: int = 0, timeout: int = 60, **kwargs) -> GetUpdatesResponse:
        """
        Функция обновления чата бота
        По истечении времени timeout перестает получать обновления
        """
        url = self.__get_url('getUpdates')
        response = requests.get(url, params={'timeout': timeout, 'offset': offset, 'allowed_updates': ['message']})

        if response.ok:
            data = response.json()
        else:
            logger.error('Bad request getUpdates, %d', response.status_code)
            data = {'ok': False, 'result': []}

        return self.__serialize_tg_response(GetUpdatesResponse, data)

    def send_message(self, chat_id: int, text: str, **kwargs) -> SendMessageResponse:
        """
        Функция отправки сообщений бота
        """
        data = self._get('sendMessage', chat_id=chat_id, text=text, **kwargs)
        return self.__serialize_tg_response(SendMessageResponse, data)

    def _get(self, method: str, **params) -> dict:
        """
        Вспомогательная функция для получения запроса из сообщения
        """
        url = self.__get_url(method)
        params.setdefault('timeout', 10)
        response = requests.get(url, params=params)
        if not response.ok:
            logger.warning('Invalid status code %d from command %s', response.status_code, method)
        response.json()
        return response.json()

    @staticmethod
    def __serialize_tg_response(serializer_class: Type[T], data: dict) -> T:
        """
        Вспомогательная функция. Подставляет сериализатор с данными пришедшими на вход
        """
        try:
            return serializer_class(**data)
        except ValidationError:
            logger.error(f'Failed to serialize JSON response: {data}')
