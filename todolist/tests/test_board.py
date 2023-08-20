import pytest
from django.urls import reverse
from goals.models import Board, BoardParticipant


@pytest.mark.django_db
class TestBoardList:
    url = reverse('goals:board-list')

    def test_get_board_list_fail(self, client, faker):
        """
        Не аутентифицированным пользователям просматривать доски нельзя
        """
        result = client.get(self.url)
        assert result.status_code == 403

    def test_get_board_list(self, auto_login_user, faker):
        """
        Аутентифицированные пользователи получают список досок
        """
        response = auto_login_user.get(self.url)
        assert response.status_code == 200

    def test_get_board_list_not_participant(self, auto_login_user, faker):
        """
        Аутентифицированные пользователи получают список досок, но не являются их владельцами
        """

        response = auto_login_user.get(self.url)
        assert response.status_code == 200
        assert response.data == []


@pytest.mark.django_db
class TestBoardCreated:
    url_create = reverse('goals:board-create')

    def test_created_board_not_auth(self, client, faker):
        """
        Доску создать не аутентифицированным пользователям нельзя
        """
        response = client.post(self.url_create, data={'title': 'Test_title'})
        assert response.status_code == 403

    def test_created_board_auth(self, auto_login_user, faker):
        """
        Аутентифицированный пользователь может создать доску.
        Проверка, что роль - владелец (role - 1)
        """
        response = auto_login_user.post(self.url_create, data={'title': 'Test_Board_created'})
        current_user = response.wsgi_request.user
        created_board = Board.objects.get(pk=response.data['id'])
        owner = BoardParticipant.objects.get(board_id=created_board.pk)

        assert response.status_code == 201
        assert current_user == owner.user
