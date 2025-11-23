from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from events.models import Location


class LocationAPITests(APITestCase):
    def setUp(self):
        Location.objects.create(name='hall_a', capacity=50)
        Location.objects.create(name='auditorium', capacity=300)
        Location.objects.create(name='hall_b', capacity=75)

    def test_list_locations_without_authentication(self):
        response = self.client.get(reverse('location-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertTrue(len(response.data) >= 3)

    def test_get_location_detail_without_authentication(self):
        location = Location.objects.first()
        response = self.client.get(reverse('location-detail', args=[location.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(location.id))
        self.assertEqual(response.data['name'], location.name)

    def test_location_serializer_includes_all_fields(self):
        location = Location.objects.first()
        response = self.client.get(reverse('location-detail', args=[location.id]))
        self.assertIn('id', response.data)
        self.assertIn('name', response.data)
        self.assertIn('location_display', response.data)
        self.assertIn('capacity', response.data)

    def test_location_display_field_is_correct(self):
        location = Location.objects.get(name='hall_a')
        response = self.client.get(reverse('location-detail', args=[location.id]))
        self.assertEqual(response.data['location_display'], 'Hall A')

    def test_all_locations_have_capacity(self):
        response = self.client.get(reverse('location-list'))
        for location_data in response.data:
            self.assertIn('capacity', location_data)
            self.assertIsInstance(location_data['capacity'], int)
            self.assertGreater(location_data['capacity'], 0)

    def test_locations_are_read_only(self):
        location = Location.objects.first()
        payload = {
            'name': 'hall_c',
            'capacity': 100
        }
        response = self.client.post(reverse('location-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(reverse('location-detail', args=[location.id]), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(reverse('location-detail', args=[location.id]))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

