import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    def authenticate(is_staff=False, user=None):
        if user:
            return api_client.force_authenticate(user=user)
        return api_client.force_authenticate(user=User(is_staff=is_staff))

    return authenticate
