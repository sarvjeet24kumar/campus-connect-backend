from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User, Role, UserRole


class LoginAPITests(APITestCase):

    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(role="student")
        self.url = reverse("login")

    
    def test_login_success(self):
        u = User.objects.create_user(username="u1", password="pass123")
        UserRole.objects.create(user=u, role=self.student_role)
        r = self.client.post(self.url, {"username": "u1", "password": "pass123"})
        self.assertEqual(r.status_code, 200)


    
    def test_login_missing_username(self):
        r = self.client.post(self.url, {"password": "pass"})
        self.assertEqual(r.status_code, 400)

   
    def test_login_missing_password(self):
        r = self.client.post(self.url, {"username": "u"})
        self.assertEqual(r.status_code, 400)

   
    def test_login_empty_payload(self):
        r = self.client.post(self.url, {})
        self.assertEqual(r.status_code, 400)

  
    def test_login_blank_username(self):
        r = self.client.post(self.url, {"username": "", "password": "pass"})
        self.assertEqual(r.status_code, 400)

    
    def test_login_blank_password(self):
        r = self.client.post(self.url, {"username": "u", "password": ""})
        self.assertEqual(r.status_code, 400)

    
    def test_login_special_characters_username(self):
        u = User.objects.create_user(username="user$", password="pass123")
        UserRole.objects.create(user=u, role=self.student_role)
        r = self.client.post(self.url, {"username": "user$", "password": "pass123"})
        self.assertEqual(r.status_code, 200)

    
    def test_login_whitespace_username(self):
        r = self.client.post(self.url, {"username": "   ", "password": "pass"})
        self.assertEqual(r.status_code, 400)

    
