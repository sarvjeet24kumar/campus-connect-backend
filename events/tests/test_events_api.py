from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role, User, UserRole
from events.models import Location


class EventsAPITests(APITestCase):
    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(role='student')
        self.admin_role, _ = Role.objects.get_or_create(role='admin')
        self.super_admin_role, _ = Role.objects.get_or_create(role='super_admin')

        self.location = Location.objects.create(name='hall_a', capacity=100)

        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin_test@example.com',
            password='admintestpass'
        )
        UserRole.objects.create(user=self.admin_user, role=self.admin_role)
    def _create_future_event_payload(self):
        start = timezone.now() + timedelta(days=2)
        end = start + timedelta(hours=2)
        return {
            'title': 'Freshers party',
            'description': 'Just welcome the new batches',
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'location': self.location.id,
            'seats': 50,
        }

    def test_admin_cannot_create_past_event(self):
        self.client.force_authenticate(user=self.admin_user)

        past_start = timezone.now() - timedelta(days=1)
        past_end = past_start + timedelta(hours=1)
        payload = {
            'title': 'Past Event',
            'description': 'Should not be allowed',
            'start_time': past_start.isoformat(),
            'end_time': past_end.isoformat(),
            'location': self.location.id,
            'seats': 30,
        }

        response = self.client.post(reverse('event-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        detail = response.data
        if isinstance(detail, dict):
            messages = []
            for value in detail.values():
                if isinstance(value, list):
                    messages.extend(value)
                else:
                    messages.append(str(value))
        elif isinstance(detail, list):
            messages = detail
        else:
            messages = [str(detail)]

        self.assertTrue(any('future' in message.lower() for message in messages))
