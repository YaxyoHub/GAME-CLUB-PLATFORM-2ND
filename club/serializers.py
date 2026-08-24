from rest_framework import serializers
from .models import Club

class ClubSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    calculated_distance_km = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Club
        fields = [
            'id', 'owner', 'owner_username', 'name', 'region', 'city', 'address', 
            'latitude', 'longitude', 'phone', 'phone2', 'description', 
            'profile_photo', 'working_hours_from', 'working_hours_to', 
            'is_active', 'created_at', 'calculated_distance_km'
        ]
        extra_kwargs = {
            'owner': {'read_only': True},
            'latitude': {'required': True},
            'longitude': {'required': True},
        }

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude -90 va 90 oralig'ida bo'lishi kerak.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude -180 va 180 oralig'ida bo'lishi kerak.")
        return value
