import pytest
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_user_creation():
    u = User.objects.create_user(username="user", password="123")
    assert u.username == "user"
