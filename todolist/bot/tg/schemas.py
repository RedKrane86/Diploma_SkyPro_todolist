from pydantic import BaseModel


class Chat(BaseModel):
    """
    Класс чата
    """
    id: int
    username: str | None = None


class Message(BaseModel):
    """
    Класс сообщений
    """
    message_id: int
    chat: Chat
    text: str


class UpdateObj(BaseModel):
    """
    Класс обновления состояния чата
    """
    update_id: int
    message: Message


class GetUpdatesResponse(BaseModel):
    """
    Класс получения обновлений чата
    """
    ok: bool
    result: list[UpdateObj] = []


class SendMessageResponse(BaseModel):
    """
    Класс отправки сообщений
    """
    ok: bool
    result: Message
