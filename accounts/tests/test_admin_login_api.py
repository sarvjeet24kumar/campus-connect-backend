from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User, Role, UserRole


class AdminLoginTests(APITestCase):

    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(role="student")
        self.admin_role, _ = Role.objects.get_or_create(role="admin")
        self.super_role, _ = Role.objects.get_or_create(role="super_admin")
        self.url = reverse("login")

    def test_admin_login_success(self):
        u = User.objects.create_user(username="adm", password="pass123")
        UserRole.objects.create(user=u, role=self.admin_role)
        r = self.client.post(self.url, {"username": "adm", "password": "pass123", "is_admin": True})
        self.assertEqual(r.status_code, 200)


    def test_admin_login_requires_role(self):
        u = User.objects.create_user(username="norole", password="pass123")
        r = self.client.post(self.url, {"username": "norole", "password": "pass123", "is_admin": True})
        self.assertEqual(r.status_code, 403)

    def test_student_cannot_login_as_admin(self):
        u = User.objects.create_user(username="stu1", password="pass123")
        UserRole.objects.create(user=u, role=self.student_role)
        r = self.client.post(self.url, {"username": "stu1", "password": "pass123", "is_admin": True})
        self.assertEqual(r.status_code, 403)

    def test_super_admin_login_success(self):
        u = User.objects.create_user(username="super", password="pass123")
        UserRole.objects.create(user=u, role=self.super_role)
        r = self.client.post(self.url, {"username": "super", "password": "pass123", "is_admin": True})
        self.assertEqual(r.status_code, 200)


    def test_admin_login_wrong_password(self):
        u = User.objects.create_user(username="adw", password="correct")
        UserRole.objects.create(user=u, role=self.admin_role)
        r = self.client.post(self.url, {"username": "adw", "password": "wrong", "is_admin": True})
        self.assertEqual(r.status_code, 400)


    def test_admin_login_nonexistent_user(self):
        r = self.client.post(self.url, {"username": "ghost", "password": "x", "is_admin": True})
        self.assertEqual(r.status_code, 400)

  
    def test_admin_flag_false_allows_student(self):
        u = User.objects.create_user(username="stu2", password="pass123")
        UserRole.objects.create(user=u, role=self.student_role)
        r = self.client.post(self.url, {"username": "stu2", "password": "pass123"})
        self.assertEqual(r.status_code, 200)


    def test_admin_flag_missing_treated_as_normal_login(self):
        u = User.objects.create_user(username="adm2", password="pass123")
        UserRole.objects.create(user=u, role=self.admin_role)
        r = self.client.post(self.url, {"username": "adm2", "password": "pass123"})
        self.assertEqual(r.status_code, 200)

    
    def test_student_login_with_admin_flag_blocked(self):
        u = User.objects.create_user(username="xstu", password="pass123")
        UserRole.objects.create(user=u, role=self.student_role)
        r = self.client.post(self.url, {"username": "xstu", "password": "pass123", "is_admin": True})
        self.assertEqual(r.status_code, 403)

  
    def test_admin_login_returns_roles(self):
        u = User.objects.create_user(username="admininfo", password="pass123")
        UserRole.objects.create(user=u, role=self.admin_role)
        r = self.client.post(self.url, {"username": "admininfo", "password": "pass123", "is_admin": True})
        self.assertIn("roles", r.data)

    def test_super_admin_has_access_to_admin_login(self):
        u = User.objects.create_user(username="su111", password="x")
        UserRole.objects.create(user=u, role=self.super_role)
        r = self.client.post(self.url, {"username": "su111", "password": "x", "is_admin": True})
        self.assertEqual(r.status_code, 200)


    def test_super_admin_standard_login(self):
        u = User.objects.create_user(username="su2", password="pass")
        UserRole.objects.create(user=u, role=self.super_role)
        r = self.client.post(self.url, {"username": "su2", "password": "pass"})
        self.assertEqual(r.status_code, 200)

    def test_admin_cannot_login_with_blank_password(self):
        u = User.objects.create_user(username="bladmin", password="abc123")
        UserRole.objects.create(user=u, role=self.admin_role)
        r = self.client.post(self.url, {"username": "bladmin", "password": "", "is_admin": True})
        self.assertEqual(r.status_code, 400)


    def test_admin_login_requires_json(self):
        u = User.objects.create_user(username="jsonadm", password="x")
        UserRole.objects.create(user=u, role=self.admin_role)
        r = self.client.post(self.url, "plain", content_type="text/plain")
        self.assertIn(r.status_code, [400, 415])

  
    def test_admin_login_does_not_expose_password(self):
        u = User.objects.create_user(username="nopassadm", password="asd123")
        UserRole.objects.create(user=u, role=self.admin_role)
        r = self.client.post(self.url, {"username": "nopassadm", "password": "asd123", "is_admin": True})
        self.assertNotIn("password", str(r.data))

   
    def test_admin_login_roles_must_include_admin(self):
        u = User.objects.create_user(username="none1", password="p")
        r = self.client.post(self.url, {"username": "none1", "password": "p", "is_admin": True})
        self.assertEqual(r.status_code, 403)

  
    def test_admin_login_fails_empty_payload(self):
        r = self.client.post(self.url, {"is_admin": True})
        self.assertEqual(r.status_code, 400)


    def test_admin_login_username_case_sensitive(self):
        u = User.objects.create_user(username="AdminCase", password="x")
        UserRole.objects.create(user=u, role=self.admin_role)
        r = self.client.post(self.url, {"username": "admincase", "password": "x", "is_admin": True})
        self.assertEqual(r.status_code, 400)

  
    