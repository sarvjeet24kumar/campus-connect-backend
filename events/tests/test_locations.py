# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase, APIClient

# from events.models import Location


# class LocationAPITests(APITestCase):
#     def setUp(self):
#         # create a couple of locations
#         Location.objects.create(name='hall_a', capacity=50)
#         Location.objects.create(name='auditorium', capacity=300)
#         self.client = APIClient()

#     def test_list_locations(self):
#         url = reverse('location-list')
#         resp = self.client.get(url)
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         data = resp.json()
#         # there should be at least the two locations we created
#         self.assertTrue(isinstance(data, list))
#         names = {item.get('name') for item in data}
#         self.assertIn('hall_a', names)
#         self.assertIn('auditorium', names)

#     def test_location_fields(self):
#         url = reverse('location-list')
#         resp = self.client.get(url)
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         item = resp.json()[0]
#         # ensure serializer returns expected fields
#         self.assertIn('id', item)
#         self.assertIn('name', item)
#         self.assertIn('capacity', item)
#         self.assertIn('location_display', item)
