from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EventViewSet, LocationViewSet, RegistrationViewSet

router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'registrations', RegistrationViewSet, basename='registration')
router.register(r'', EventViewSet, basename='event') 

urlpatterns = [
    path('', include(router.urls)),
]

