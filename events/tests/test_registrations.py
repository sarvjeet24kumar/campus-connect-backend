# from datetime import timedelta
# from django.urls import reverse
# from django.utils import timezone
# from django.contrib.auth import get_user_model

# from rest_framework import status
# from rest_framework.test import APITestCase, APIClient

# from accounts.models import Role
# from events.models import Location, Event, Registration

# User = get_user_model()


# def assign_role_to_user(user, role):
#     try:
#         setattr(user, 'role', role)
#         user.save()
#         return
#     except Exception:
#         pass
#     try:
#         user.user_roles.create(role=role)
#         return
#     except Exception:
#         pass
#     try:
#         user.roles.add(role)
#         return
#     except Exception:
#         pass


# class RegistrationsAPITests(APITestCase):
#     def setUp(self):
#         self.student_role, _ = Role.objects.get_or_create(role='student')
#         self.admin_role, _ = Role.objects.get_or_create(role='admin')

#         User.objects.create_user(
#         username='admin_test',
#         email='admin_test@example.com',
#         password='admintestpass'
#             )
#         assign_role_to_user(self.admin_user, self.admin_role)

#         User.objects.create_user(
#             username='student_test',
#             email='student_test@example.com',
#             password='studentpass'
#         )

#         assign_role_to_user(self.student_user, self.student_role)

#         self.location = Location.objects.create(name='hall_a', capacity=10)

#         # create an event (admin)
#         start = timezone.now() + timedelta(days=1)
#         end = start + timedelta(hours=2)
#         self.event = Event.objects.create(
#             title='Registrations Event',
#             description='For registration tests',
#             start_time=start,
#             end_time=end,
#             location=self.location,
#             seats=5,
#             created_by=self.admin_user
#         )

#         self.client = APIClient()

#     def test_admin_cannot_register(self):
#         self.client.force_authenticate(user=self.admin_user)
#         payload = {'event': str(self.event.id)}
#         resp = self.client.post(reverse('registration-list'), payload, format='json')
#         self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

#     def test_student_can_register_and_unregister(self):
#         # student registers
#         self.client.force_authenticate(user=self.student_user)
#         payload = {'event': str(self.event.id)}
#         resp = self.client.post(reverse('registration-list'), payload, format='json')
#         self.assertEqual(resp.status_code, status.HTTP_201_CREATED, msg=resp.data)

#         registration_id = resp.json().get('id')

#         # student can view their registrations
#         self.client.force_authenticate(user=self.student_user)
#         my_regs = self.client.get(reverse('registration-my-registrations'))
#         self.assertEqual(my_regs.status_code, status.HTTP_200_OK)
#         self.assertTrue(any(r.get('id') == registration_id for r in my_regs.json()))

#         # unregister
#         self.client.force_authenticate(user=self.student_user)
#         unregister_url = reverse('registration-unregister', kwargs={'pk': registration_id})
#         unreg_resp = self.client.post(unregister_url)
#         self.assertEqual(unreg_resp.status_code, status.HTTP_200_OK)
#         # ensure registration is deleted
#         self.assertFalse(Registration.objects.filter(id=registration_id).exists())

#     def test_cannot_register_if_no_seats(self):
#         # fill seats
#         self.client.force_authenticate(user=self.student_user)
#         for i in range(self.event.seats):
#             u = User.objects.create_user(username=f'st_{i}', password='pass')
#             assign_role_to_user(u, self.student_role)
#             self.client.force_authenticate(user=u)
#             r = self.client.post(reverse('registration-list'), {'event': str(self.event.id)}, format='json')
#             self.assertEqual(r.status_code, status.HTTP_201_CREATED, msg=r.data)

#         # another student tries to register
#         last_student = User.objects.create_user(username='late_student', password='pass')
#         assign_role_to_user(last_student, self.student_role)
#         self.client.force_authenticate(user=last_student)
#         r2 = self.client.post(reverse('registration-list'), {'event': str(self.event.id)}, format='json')
#         self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)
