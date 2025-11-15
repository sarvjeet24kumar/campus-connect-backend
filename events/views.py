from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from .models import Event, Location, Registration
from .serializers import EventSerializer, LocationSerializer, RegistrationSerializer, StudentRegistrationSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(deleted_at__isnull=True).order_by('-start_time')
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_type = self.request.query_params.get('filter')
        if filter_type == 'upcoming':
            queryset = queryset.filter(start_time__gte=timezone.now())
        elif filter_type == 'past':
            queryset = queryset.filter(start_time__lt=timezone.now())
        return queryset

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied

        if not self.request.user.is_authenticated:
            raise PermissionDenied('Authentication required')

        user_roles = [user_role.role.role for user_role in self.request.user.user_roles.all()]
        if 'admin' not in user_roles and 'super_admin' not in user_roles:
            raise PermissionDenied('Only admins can create events')

        try:
            serializer.save(created_by=self.request.user)
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.messages)

    def perform_update(self, serializer):
        from rest_framework.exceptions import PermissionDenied

        if not self.request.user.is_authenticated:
            raise PermissionDenied('Authentication required')

        user_roles = [user_role.role.role for user_role in self.request.user.user_roles.all()]
        if 'admin' not in user_roles and 'super_admin' not in user_roles:
            raise PermissionDenied('Only admins can update events')

        event = self.get_object()
        if event.created_by != self.request.user:
            raise PermissionDenied('You can only update events created by you')

        try:
            serializer.save()
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.messages)
    
    @action(detail=True, methods=['post', 'delete'])
    def soft_delete(self, request, pk=None):
        event = self.get_object()
        user_roles = [user_role.role.role for user_role in request.user.user_roles.all()]

        if 'admin' not in user_roles and 'super_admin' not in user_roles:
            return Response({'error': 'Only admins can delete events'}, status=status.HTTP_403_FORBIDDEN)

        if event.created_by != request.user:
            return Response({'error': 'You can only delete events created by you'}, status=status.HTTP_403_FORBIDDEN)

        event.deleted_at = timezone.now()
        event.deleted_by = request.user
        event.save()

        Registration.objects.filter(event=event).delete()

        return Response({'message': 'Event deleted successfully'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def registrations(self, request, pk=None):
        event = self.get_object()
        user_roles = [user_role.role.role for user_role in request.user.user_roles.all()]

        if 'admin' not in user_roles and 'super_admin' not in user_roles:
            return Response({'error': 'Only admins can view registrations'}, status=status.HTTP_403_FORBIDDEN)

        registrations = Registration.objects.filter(event=event, status='registered')
        serializer = RegistrationSerializer(registrations, many=True)
        return Response(serializer.data)


class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_roles = [user_role.role.role for user_role in self.request.user.user_roles.all()]
        if 'admin' in user_roles or 'super_admin' in user_roles:
            return Registration.objects.all()
        return Registration.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError

        user_roles = [user_role.role.role for user_role in self.request.user.user_roles.all()]
        if 'admin' in user_roles or 'super_admin' in user_roles:
            raise PermissionDenied('Admins cannot register for events')

        event = serializer.validated_data['event']

        if event.start_time < timezone.now():
            raise DRFValidationError('Cannot register for past events')

        if Registration.objects.filter(event=event, student=self.request.user).exists():
            raise DRFValidationError('Already registered for this event')

        if event.available_seats <= 0:
            raise DRFValidationError('No seats available for this event')

        serializer.save(student=self.request.user, status='registered')

    @action(detail=True, methods=['post'])
    def unregister(self, request, pk=None):
        """Unregister from an event"""
        registration = self.get_object()

        if registration.student != request.user:
            return Response({'error': 'You can only unregister from your own registrations'}, status=status.HTTP_403_FORBIDDEN)

        registration.delete()
        return Response({'message': 'Successfully unregistered from event'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def my_registrations(self, request):
        """Get current user's registrations with event details"""
        registrations = Registration.objects.filter(student=request.user, status='registered')
        serializer = StudentRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)

