from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4)
    email = models.EmailField(unique=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Role(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]
    id=models.UUIDField(primary_key=True,default=uuid.uuid4)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.get_role_display()


class UserRole(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # unique_together = ('user', 'role')
        constraints = [
        models.UniqueConstraint(
            fields=['user', 'role'],
            name='unique_user_role'
        )
        ]   

    def __str__(self):
        return f"{self.user.username} - {self.role.role}"




