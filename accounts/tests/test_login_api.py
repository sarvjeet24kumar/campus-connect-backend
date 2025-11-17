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

   
    def test_login_wrong_password(self):
        u = User.objects.create_user(username="u2", password="correct")
        r = self.client.post(self.url, {"username": "u2", "password": "wrong"})
        self.assertEqual(r.status_code, 400)

  
    def test_login_non_existing_user(self):
        r = self.client.post(self.url, {"username": "ghost", "password": "pass"})
        self.assertEqual(r.status_code, 400)

   
    def test_login_user_with_no_roles(self):
        User.objects.create_user(username="norole", password="pass123")
        r = self.client.post(self.url, {"username": "norole", "password": "pass123"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["roles"], [])

   
    def test_login_returns_tokens(self):
        u = User.objects.create_user(username="tok", password="pass123")
        UserRole.objects.create(user=u, role=self.student_role)
        r = self.client.post(self.url, {"username": "tok", "password": "pass123"})
        self.assertIn("access", r.data["tokens"])

    
    def test_login_missing_username(self):
        r = self.client.post(self.url, {"password": "pass"})
        self.assertEqual(r.status_code, 400)

   
    def test_login_missing_password(self):
        r = self.client.post(self.url, {"username": "u"})
        self.assertEqual(r.status_code, 400)

   
    def test_login_empty_payload(self):
        r = self.client.post(self.url, {})
        self.assertEqual(r.status_code, 400)

    
    def test_login_sql_injection(self):
        r = self.client.post(self.url, {"username": "' OR 1=1 --", "password": "x"})
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

    
    def test_login_case_sensitivity(self):
        User.objects.create_user(username="CaseUser", password="pass123")
        r = self.client.post(self.url, {"username": "caseuser", "password": "pass123"})
        self.assertEqual(r.status_code, 400)

    
    def test_login_long_username(self):
        long = "a" * 200
        User.objects.create_user(username="short", password="pass123")
        r = self.client.post(self.url, {"username": long, "password": "pass123"})
        self.assertEqual(r.status_code, 400)

    
    def test_login_requires_json(self):
        r = self.client.post(self.url, "text", content_type="text/plain")
        self.assertIn(r.status_code, [400, 415])

    def test_login_returns_role_list(self):
        u = User.objects.create_user(username="rlist", password="pass123")
        UserRole.objects.create(user=u, role=self.student_role)
        r = self.client.post(self.url, {"username": "rlist", "password": "pass123"})
        self.assertIn("roles", r.data)

    
    def test_login_incorrect_email_not_allowed(self):
        u = User.objects.create_user(username="emailtest", email="e@mail.com", password="pass123")
        r = self.client.post(self.url, {"username": "e@mail.com", "password": "pass123"})
        self.assertEqual(r.status_code, 400)

    
    def test_login_whitespace_username(self):
        r = self.client.post(self.url, {"username": "   ", "password": "pass"})
        self.assertEqual(r.status_code, 400)

    
    def test_login_unicode_username(self):
        u = User.objects.create_user(username="ユーザー", password="pass123")
        UserRole.objects.create(user=u, role=self.student_role)
        r = self.client.post(self.url, {"username": "ユーザー", "password": "pass123"})
        self.assertEqual(r.status_code, 200)

    
    def test_login_does_not_expose_password(self):
        u = User.objects.create_user(username="safe", password="pass123")
        UserRole.objects.create(user=u, role=self.student_role)
        r = self.client.post(self.url, {"username": "safe", "password": "pass123"})
        self.assertNotIn("password", str(r.data))
