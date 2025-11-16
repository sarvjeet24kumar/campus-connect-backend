from rest_framework import serializers
from .models import Event, Location, Registration


class LocationSerializer(serializers.ModelSerializer):
    location_display = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Location
        fields = ('id', 'name', 'location_display', 'capacity')


class EventSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    registered_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'start_time', 'end_time', 'location',
            'location_name', 'seats', 'available_seats', 'created_by', 'created_by_name',
            'is_past', 'registered_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def get_registered_count(self, obj):
        return obj.registrations.filter(status='registered').count()

    def validate(self, data):
        location = data.get('location') or getattr(self.instance, 'location', None)
        seats = data.get('seats') or getattr(self.instance, 'seats', None)

        if location and seats: 
            if seats > location.capacity:
                raise serializers.ValidationError(
                    {"seats": f"Seats ({seats}) cannot exceed location capacity ({location.capacity})."}
                )

        return data

class RegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    student_name = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = Registration
        fields = ('id', 'event', 'event_title', 'student', 'student_name', 'status', 'created_at')
        read_only_fields = ('student', 'created_at')


class StudentRegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ('id', 'event', 'status', 'created_at')
        read_only_fields = ("event", "created_at")
