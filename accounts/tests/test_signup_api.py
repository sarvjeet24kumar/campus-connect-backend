from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User, Role, UserRole


class SignupAPITests(APITestCase):

    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(role="student")
        self.url = reverse("signup")


    def test_signup_missing_username(self):
        payload = {"email": "x@mail.com", "password": "pass123", "password_confirm": "pass123"}
        r = self.client.post(self.url, payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_signup_missing_email(self):
        payload = {"username": "u1", "password": "pass123", "password_confirm": "pass123"}
        r = self.client.post(self.url, payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_signup_password_mismatch(self):
        payload = {
            "username": "user2",
            "email": "user2@mail.com",
            "password": "pass123",
            "password_confirm": "notmatch",
        }
        r = self.client.post(self.url, payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


    def test_signup_existing_username(self):
        User.objects.create_user(username="bob", email="b@mail.com", password="123")
        payload = {
            "username": "bob",
            "email": "new@mail.com",
            "password": "pass12345",
            "password_confirm": "pass12345"
        }
        r = self.client.post(self.url, payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

   
    def test_signup_existing_email(self):
        User.objects.create_user(username="u3", email="taken@mail.com", password="123")
        payload = {
            "username": "newUser",
            "email": "taken@mail.com",
            "password": "pass12345",
            "password_confirm": "pass12345"
        }
        r = self.client.post(self.url, payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_invalid_email(self):
        payload = {
            "username": "bademail",
            "email": "wrongformat",
            "password": "pass12345",
            "password_confirm": "pass12345"
        }
        r = self.client.post(self.url, payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_signup_blank_password(self):
        payload = {
            "username": "blankpass",
            "email": "b@mail.com",
            "password": "",
            "password_confirm": "",
        }
        r = self.client.post(self.url, payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_signup_password_too_short(self):
        payload = {
            "username": "short",
            "email": "short@mail.com",
            "password": "12",
            "password_confirm": "12",
        }
        r = self.client.post(self.url, payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_signup_long_username(self):
        payload = {
            "username": "a" * 200,
            "email": "long@mail.com",
            "password": "pass12345",
            "password_confirm": "pass12345",
        }
        r = self.client.post(self.url, payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

   
    def test_signup_long_email(self):
        payload = {
            "username": "normaluser",
            "email": ("a" * 300) + "@mail.com",
            "password": "pass12345",
            "password_confirm": "pass12345"
        }
        r = self.client.post(self.url)
        self.assertIn(r.status_code, [400, 413])

    
    def test_signup_without_password_confirm(self):
        payload = {
            "username": "no_confirm",
            "email": "no@mail.com",
            "password": "pass12345",
        }
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 400)

   
    def test_signup_empty_payload(self):
        r = self.client.post(self.url, {})
        self.assertEqual(r.status_code, 400)

   
    def test_signup_username_with_spaces(self):
        payload = {
            "username": "user name",
            "email": "t@mail.com",
            "password": "pass12345",
            "password_confirm": "pass12345"
        }
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 400)

    
    def test_signup_email_with_spaces(self):
        payload = {
            "username": "test11",
            "email": "test mail.com",
            "password": "pass12345",
            "password_confirm": "pass12345"
        }
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 400)

   
    def test_signup_requires_json(self):
        r = self.client.post(self.url, "plain text", content_type="text/plain")
        self.assertIn(r.status_code, [400, 415])

   
    
