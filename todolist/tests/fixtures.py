import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def auto_login_user(client: APIClient, user) -> APIClient:
    client.force_authenticate(user)
    return client
