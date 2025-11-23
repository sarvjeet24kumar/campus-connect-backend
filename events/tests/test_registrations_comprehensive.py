from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role, User, UserRole
from events.models import Event, Location, Registration


class RegistrationsAPITests(APITestCase):
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

        start = timezone.now() + timedelta(days=2)
        end = start + timedelta(hours=2)
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            start_time=start,
            end_time=end,
            location=self.location,
            seats=50,
            created_by=self.admin_user
        )

    def test_student_can_register_for_event(self):
        self.client.force_authenticate(user=self.student_user)
        payload = {'event': self.event.id}
        response = self.client.post(reverse('registration-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data['event']), str(self.event.id))
        self.assertEqual(str(response.data['student']), str(self.student_user.id))

    def test_admin_cannot_register_for_event(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {'event': self.event.id}
        response = self.client.post(reverse('registration-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_student_cannot_register_for_past_event(self):
        other_location = Location.objects.create(name='hall_b', capacity=50)
        future_start = timezone.now() + timedelta(days=5)
        future_end = future_start + timedelta(hours=2)
        past_event = Event.objects.create(
            title='Past Event',
            description='Past Description',
            start_time=future_start,
            end_time=future_end,
            location=other_location,
            seats=50,
            created_by=self.admin_user
        )
        past_start = timezone.now() - timedelta(days=1)
        past_end = past_start + timedelta(hours=1)
        Event.objects.filter(id=past_event.id).update(start_time=past_start, end_time=past_end)
        past_event.refresh_from_db()

        self.client.force_authenticate(user=self.student_user)
        payload = {'event': past_event.id}
        response = self.client.post(reverse('registration-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_cannot_register_when_no_seats_available(self):
        other_location = Location.objects.create(name='hall_b', capacity=50)
        small_event = Event.objects.create(
            title='Small Event',
            description='Only 1 seat',
            start_time=timezone.now() + timedelta(days=3),
            end_time=timezone.now() + timedelta(days=3, hours=2),
            location=other_location,
            seats=1,
            created_by=self.admin_user
        )

        student2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='student2pass'
        )
        UserRole.objects.create(user=student2, role=self.student_role)

        self.client.force_authenticate(user=self.student_user)
        payload = {'event': small_event.id}
        first_response = self.client.post(reverse('registration-list'), payload, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=student2)
        second_response = self.client.post(reverse('registration-list'), payload, format='json')
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_can_view_own_registrations(self):
        self.client.force_authenticate(user=self.student_user)
        payload = {'event': self.event.id}
        self.client.post(reverse('registration-list'), payload, format='json')

        response = self.client.get(reverse('registration-my-registrations'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertTrue(len(response.data) > 0)

    def test_student_can_unregister_from_event(self):
        self.client.force_authenticate(user=self.student_user)
        payload = {'event': self.event.id}
        register_response = self.client.post(reverse('registration-list'), payload, format='json')
        registration_id = register_response.data['id']

        unregister_response = self.client.post(reverse('registration-unregister', args=[registration_id]))
        self.assertEqual(unregister_response.status_code, status.HTTP_200_OK)
        self.assertEqual(unregister_response.data['message'], 'Successfully unregistered from event')

        self.assertFalse(Registration.objects.filter(id=registration_id).exists())

    def test_admin_can_view_all_registrations(self):
        self.client.force_authenticate(user=self.student_user)
        payload = {'event': self.event.id}
        self.client.post(reverse('registration-list'), payload, format='json')

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('registration-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertTrue(len(response.data) > 0)

    def test_student_can_only_view_own_registrations(self):
        student2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='student2pass'
        )
        UserRole.objects.create(user=student2, role=self.student_role)

        self.client.force_authenticate(user=self.student_user)
        payload = {'event': self.event.id}
        self.client.post(reverse('registration-list'), payload, format='json')

        self.client.force_authenticate(user=student2)
        response = self.client.get(reverse('registration-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
