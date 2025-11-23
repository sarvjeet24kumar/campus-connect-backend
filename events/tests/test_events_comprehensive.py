from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role, User, UserRole
from events.models import Event, Location


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

        self.student_user = User.objects.create_user(
            username='student_test',
            email='student_test@example.com',
            password='studentpass'
        )
        UserRole.objects.create(user=self.student_user, role=self.student_role)

    def _create_future_event_payload(self):
        start = timezone.now() + timedelta(days=2)
        end = start + timedelta(hours=2)
        return {
            'title': 'Future Event',
            'description': 'An event scheduled in the future',
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'location': self.location.id,
            'seats': 50,
        }

    def test_list_events_without_authentication(self):
        response = self.client.get(reverse('event-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_event_detail_without_authentication(self):
        self.client.force_authenticate(user=self.admin_user)
        create_payload = self._create_future_event_payload()
        create_response = self.client.post(reverse('event-list'), create_payload, format='json')
        event_id = create_response.data['id']
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse('event-detail', args=[event_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], create_payload['title'])

    def test_admin_can_create_event(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = self._create_future_event_payload()
        response = self.client.post(reverse('event-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], payload['title'])

    def test_student_cannot_create_event(self):
        self.client.force_authenticate(user=self.student_user)
        payload = self._create_future_event_payload()
        response = self.client.post(reverse('event-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_create_event(self):
        payload = self._create_future_event_payload()
        response = self.client.post(reverse('event-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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

    def test_admin_cannot_create_event_with_end_time_before_start_time(self):
        self.client.force_authenticate(user=self.admin_user)
        start = timezone.now() + timedelta(days=2)
        end = start - timedelta(hours=1)
        payload = {
            'title': 'Invalid Event',
            'description': 'End before start',
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'location': self.location.id,
            'seats': 30,
        }
        response = self.client.post(reverse('event-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_create_event_with_seats_exceeding_capacity(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = self._create_future_event_payload()
        payload['seats'] = 200
        response = self.client.post(reverse('event-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_update_own_event(self):
        self.client.force_authenticate(user=self.admin_user)
        create_payload = self._create_future_event_payload()
        create_response = self.client.post(reverse('event-list'), create_payload, format='json')
        event_id = create_response.data['id']

        update_payload = {
            'title': 'Updated Event Title',
            'description': create_payload['description'],
            'start_time': create_payload['start_time'],
            'end_time': create_payload['end_time'],
            'location': self.location.id,
            'seats': create_payload['seats'],
        }
        response = self.client.put(reverse('event-detail', args=[event_id]), update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Event Title')

    def test_admin_cannot_update_other_admin_event(self):
        self.client.force_authenticate(user=self.admin_user)
        create_payload = self._create_future_event_payload()
        create_response = self.client.post(reverse('event-list'), create_payload, format='json')
        event_id = create_response.data['id']

        other_admin = User.objects.create_user(
            username='other_admin',
            email='other_admin@example.com',
            password='otherpass'
        )
        UserRole.objects.create(user=other_admin, role=self.admin_role)

        self.client.force_authenticate(user=other_admin)
        update_payload = {
            'title': 'Hacked Title',
            'description': create_payload['description'],
            'start_time': create_payload['start_time'],
            'end_time': create_payload['end_time'],
            'location': self.location.id,
            'seats': create_payload['seats'],
        }
        response = self.client.put(reverse('event-detail', args=[event_id]), update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_upcoming_events(self):
        self.client.force_authenticate(user=self.admin_user)
        create_payload = self._create_future_event_payload()
        self.client.post(reverse('event-list'), create_payload, format='json')
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse('event-list') + '?filter=upcoming')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_filter_past_events(self):
        response = self.client.get(reverse('event-list') + '?filter=past')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_soft_delete_own_event(self):
        self.client.force_authenticate(user=self.admin_user)
        create_payload = self._create_future_event_payload()
        create_response = self.client.post(reverse('event-list'), create_payload, format='json')
        event_id = create_response.data['id']

        response = self.client.post(reverse('event-soft-delete', args=[event_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Event deleted successfully')

        detail_response = self.client.get(reverse('event-detail', args=[event_id]))
        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_cannot_soft_delete_other_admin_event(self):
        self.client.force_authenticate(user=self.admin_user)
        create_payload = self._create_future_event_payload()
        create_response = self.client.post(reverse('event-list'), create_payload, format='json')
        event_id = create_response.data['id']

        other_admin = User.objects.create_user(
            username='other_admin',
            email='other_admin@example.com',
            password='otherpass'
        )
        UserRole.objects.create(user=other_admin, role=self.admin_role)

        self.client.force_authenticate(user=other_admin)
        response = self.client.post(reverse('event-soft-delete', args=[event_id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_event_registrations(self):
        self.client.force_authenticate(user=self.admin_user)
        create_payload = self._create_future_event_payload()
        create_response = self.client.post(reverse('event-list'), create_payload, format='json')
        event_id = create_response.data['id']

        self.client.force_authenticate(user=self.student_user)
        self.client.post(reverse('registration-list'), {'event': event_id}, format='json')

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('event-registrations', args=[event_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

    def test_student_cannot_view_event_registrations(self):
        self.client.force_authenticate(user=self.admin_user)
        create_payload = self._create_future_event_payload()
        create_response = self.client.post(reverse('event-list'), create_payload, format='json')
        event_id = create_response.data['id']

        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('event-registrations', args=[event_id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_serializer_includes_all_fields(self):
        self.client.force_authenticate(user=self.admin_user)
        create_payload = self._create_future_event_payload()
        create_response = self.client.post(reverse('event-list'), create_payload, format='json')
        event_id = create_response.data['id']
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse('event-detail', args=[event_id]))
        self.assertIn('id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('description', response.data)
        self.assertIn('start_time', response.data)
        self.assertIn('end_time', response.data)
        self.assertIn('location', response.data)
        self.assertIn('location_name', response.data)
        self.assertIn('seats', response.data)
        self.assertIn('available_seats', response.data)
        self.assertIn('created_by', response.data)
        self.assertIn('created_by_name', response.data)
        self.assertIn('is_past', response.data)
        self.assertIn('registered_count', response.data)

    def test_available_seats_decrease_after_registration(self):
        self.client.force_authenticate(user=self.admin_user)
        create_payload = self._create_future_event_payload()
        response = self.client.post(reverse('event-list'), create_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        event_id = response.data['id']

        self.client.force_authenticate(user=self.student_user)
        registration_response = self.client.post(reverse('registration-list'), {'event': event_id}, format='json')
        self.assertEqual(registration_response.status_code, status.HTTP_201_CREATED)

        event_detail_response = self.client.get(reverse('event-detail', args=[event_id]))
        self.assertEqual(event_detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(event_detail_response.data['available_seats'], create_payload['seats'] - 1)

