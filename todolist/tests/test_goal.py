import pytest
from django.urls import reverse

from tests.factories import CreateGoalRequest


@pytest.mark.django_db()
class TestCreateGoalView:
    url = reverse('goals:create-goal')

    def test_create_goal_auth_required_fail(self, client, faker):
        """
        Цель невозможно создать цель не зарегистрированным пользователям
        """
        response = client.post(self.url)
        assert response.status_code == 403

    def test_create_goal_not_owner_fail(self, auto_login_user, goal_category, faker):
        """
        Нельзя создать цель пользователю не владельцу доски
        """
        data = CreateGoalRequest.build(category=goal_category.id)
        response = auto_login_user.post(self.url, data=data)
        assert response.status_code == 403

    @pytest.mark.parametrize('role', [1, 2, 3])
    def test_create_goal_owner_or_writer(
        self,
        auto_login_user,
        board_participant,
        goal_category,
        faker,
        role
    ):
        """
        Создание цели владельцу или редактору доски
        """
        board_participant.role = role
        board_participant.save(update_fields=['role'])
        data = CreateGoalRequest.build(category=goal_category.id)
        response = auto_login_user.post(self.url, data=data)
        if role in (1, 2):
            assert response.status_code == 201
        else:
            assert response.status_code == 403

    def test_create_goal_on_deleted_category_fail(self, auto_login_user, goal_category, faker):
        """
        Нельзя создать цель в удаленной категории
        """
        goal_category.is_deleted = True
        goal_category.save(update_fields=['is_deleted'])
        data = CreateGoalRequest.build(category=goal_category.id)
        response = auto_login_user.post(self.url, data=data)
        assert response.status_code == 400

    def test_create_goal_on_existing_category(self, auto_login_user, faker):
        """
        Нельзя создать цель в несуществующей категории
        """
        data = CreateGoalRequest.build(category=1)
        response = auto_login_user.post(self.url, data=data)
        assert response.status_code == 400
