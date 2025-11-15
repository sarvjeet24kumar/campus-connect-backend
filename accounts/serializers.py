from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Role, User, UserRole
import re


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'roles', 'created_at')
        read_only_fields = ('id','username','created_at')

    def get_roles(self, obj):
        return [user_role.role.role for user_role in obj.user_roles.all()]


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField( allow_blank=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
    def validate_first_name(self, value):
        return self.validate_alpha(value,'first_name')

    def validate_last_name(self, value):
        return self.validate_alpha(value,'last_name')
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        student_role, _ = Role.objects.get_or_create(role='student')
        UserRole.objects.create(user=user, role=student_role)

        return user

    def validate_alpha(self,value,field_name):
        cleaned = value.strip()
        if cleaned == "":
            raise serializers.ValidationError(f"{field_name} cannot be empty or spaces only.")
        if len(cleaned) < 2:
            raise serializers.ValidationError(f"{field_name} must be at least 2 characters.")
        if not re.match(r'^[A-Za-z]+$', cleaned):
            raise serializers.ValidationError(f"Only alphabets are allowed in {field_name}.")

        return cleaned.capitalize()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request=request, username=username, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        attrs['user'] = user
        return attrs






