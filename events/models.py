from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
import uuid

class Location(models.Model):
    LOCATION_CHOICES = [
        ('hall_a', 'Hall A'),
        ('hall_b', 'Hall B'),
        ('hall_c', 'Hall C'),
        ('auditorium', 'Auditorium'),
        ('conference_room_1', 'Conference Room 1'),
        ('conference_room_2', 'Conference Room 2'),
        ('outdoor', 'Outdoor'),
    ]
    id=models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, unique=True)
    capacity = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_location_display()


class Event(models.Model):
    id=models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='events')
    seats = models.IntegerField() 
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_events')
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_events')
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        
        current_time = timezone.now()
        if self.start_time < current_time:
            raise ValidationError("Event start time must be in the future.")
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")
        overlapping = Event.objects.filter(
            location=self.location,
            deleted_at__isnull=True
        ).filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )

        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("Another event already exists at this location during the specified time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def available_seats(self):
        registered_count = self.registrations.filter(status='registered').count()
        return max(0, self.seats - registered_count)

    @property
    def is_past(self):
        return self.start_time < timezone.now()

    def __str__(self):
        return self.title


class Registration(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('cancelled', 'Cancelled'),
    ]
    id=models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # unique_together = ('event', 'student')
        constraints = [
        models.UniqueConstraint(
            fields=['event', 'student'],
            name='unique_event_student'
        )
        ]   

    def __str__(self):
        return f"{self.student.username} - {self.event.title}"

