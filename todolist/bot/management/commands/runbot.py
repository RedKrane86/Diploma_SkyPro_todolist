from django.core.management import BaseCommand


from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from goals.models import Goal, GoalCategory


class Command(BaseCommand):
    """
    Класс команд для бота
    """

    help = "run bot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()
        self.users_data = {}

    def handle(self, *args, **options):
        """
        Основная функция работы бота, работает через бесконечный цикл.
        Каждое новое сообщение получает индекс + 1
        """
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message):
        """
        Обработка сообщения пользователя.
            - Если пользователь не авторизован передает сообщение в функцию handle_unauthorized_user
            - Если пользователь авторизован передает сообщение в функцию handle_authorized_user

        """
        tg_user, created = TgUser.objects.get_or_create(chat_id=msg.chat.id)

        if tg_user.user:
            self.handle_authorized_user(tg_user, msg)
        else:
            self.handle_unauthorized_user(tg_user, msg)

    def handle_authorized_user(self, tg_user: TgUser, msg: Message):
        """
        Функция обработки сообщений авторизованных пользователей.
        Реагирует на три команды:
            - '/goals'  показать все цели
            - '/create' создать новую цель в существующей категории
            - '/cancel' отменить текущую операцию
        """
        commands: list = ['/goals', '/create', '/cancel']
        create_chat: dict | None = self.users_data.get(msg.chat.id, None)
        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'Доступные команды:\n/goals\n/create\n/cancel '
        )

        if msg.text == '/cancel':
            self.users_data.pop(msg.chat.id, None)
            create_chat = None
            self.tg_client.send_message(chat_id=msg.chat.id, text='Операция отменена')

        if msg.text in commands and not create_chat:
            if msg.text == '/goals':
                qs = Goal.objects.filter(
                    category__is_deleted=False, category__board__participants__user_id=tg_user.user.id
                ).exclude(status=Goal.Status.archived)
                goals = [f'{goal.id} - {goal.title}' for goal in qs]
                self.tg_client.send_message(chat_id=msg.chat.id, text='Нет целей' if not goals else '\n'.join(goals))

            if msg.text == '/create':
                categories_qs = GoalCategory.objects.filter(
                    board__participants__user_id=tg_user.user.id, is_deleted=False
                )

                categories = []
                categories_id = []
                for category in categories_qs:
                    categories.append(f'{category.id} - {category.title}')
                    categories_id.append(str(category.id))

                self.tg_client.send_message(
                    chat_id=msg.chat.id, text=f'Выберите номер категории:\n' + '\n'.join(categories)
                )
                self.users_data[msg.chat.id] = {
                    'categories': categories,
                    'categories_id': categories_id,
                    'category_id': '',
                    'goal_title': '',
                    'stage': 1,
                }
        if msg.text not in commands and create_chat:
            if create_chat['stage'] == 2:
                Goal.objects.create(
                    user_id=tg_user.user.id,
                    category_id=int(self.users_data[msg.chat.id]['category_id']),
                    title=msg.text,
                )
                self.tg_client.send_message(chat_id=msg.chat.id, text='Цель сохранена')
                self.users_data.pop(msg.chat.id, None)

            elif create_chat['stage'] == 1:
                if msg.text == '/cancel':
                    self.users_data.pop(msg.chat.id, None)
                    create_chat = None
                    self.tg_client.send_message(chat_id=msg.chat.id, text='Операция отменена')

                if msg.text in create_chat.get('categories_id', []):
                    self.tg_client.send_message(chat_id=msg.chat.id, text='Введите название цели')
                    self.users_data[msg.chat.id] = {'category_id': msg.text, 'stage': 2}
                else:
                    self.tg_client.send_message(
                        chat_id=msg.chat.id,
                        text='Введен неправильный номер категории\n' + '\n'.join(create_chat.get('категории', [])),
                    )

        if msg.text not in commands and not create_chat:
            self.tg_client.send_message(chat_id=msg.chat.id, text=f'Неизвестная команда')

    def handle_unauthorized_user(self, tg_user: TgUser, msg: Message):
        """
        Функция обработки сообщений ек авторизованных пользователей
        Генерирует код для верификации на сайте
        """
        code = tg_user.generate_verification_code()
        tg_user.verification_code = code
        tg_user.save()

        self.tg_client.send_message(chat_id=msg.chat.id, text=f'Ваш код верификации: {code}')
