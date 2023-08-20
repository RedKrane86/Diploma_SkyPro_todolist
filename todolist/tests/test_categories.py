import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestGoalCategory:
    url = reverse('goals:create-category')

    def test_create_category_not_auth_ail(self, client, board):
        """
        Не аутентифицированным пользователям создавать категории нельзя
        """
        response = client.post(self.url, data={'title': 'Test_title', 'board': board.title})
        assert response.status_code == 403

    @pytest.mark.parametrize('role', [1, 2, 3])
    def test_create_category(self, auto_login_user, board, board_participant, goal_category, role):
        """
        Создавать категории может только
            - владелец доски (role: 1)
            - редактор доски (role: 2)
        """
        board_participant.role = role
        board_participant.save()
        response = auto_login_user.post(self.url, data={'title': goal_category.title, 'board': board.pk})

        if role in (1, 2):
            assert response.status_code == 201
        else:
            assert response.status_code == 403

    @pytest.mark.parametrize('role', [1, 2, 3])
    def test_delete_goal_category(self, auto_login_user, board_participant, goal_category, role):
        """
        Удалять категории может только
            - владелец доски (role: 1)
            - редактор доски (role: 2)
        """
        response = auto_login_user.delete(f'/goals/goal_category/{goal_category.pk}')
        if board_participant.role in (1, 2):
            assert response.status_code == 204
