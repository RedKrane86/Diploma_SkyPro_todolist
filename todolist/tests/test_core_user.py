import pytest

from core.models import User


@pytest.mark.django_db
class TestUser:

    def test_user_create(self, client, faker):
        """
        Создание пользователя
        """
        User.objects.create_user('core:signup')
        assert User.objects.count() == 1

    def test_user_login_fail(self, client, faker):
        """
        Не авторизованные пользователи не могут зайти на сайт
        """
        response = client.post('core:login', data={'username': 'test_user_name', 'password': 'test_password'})
        assert response.status_code == 404
