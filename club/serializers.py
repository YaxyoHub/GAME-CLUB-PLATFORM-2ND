from rest_framework import serializers
from .models import Club, Seat, Type_Seat, Type_Room, Booking, Card, Images

class ClubSerializer(serializers.ModelSerializer):
    owner_phone = serializers.ReadOnlyField(source='owner.phone_number')
    owner_name = serializers.ReadOnlyField(source='owner.full_name')
    calculated_distance_km = serializers.FloatField(read_only=True, required=False)
    seats_count = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = [
            'id', 'owner', 'owner_phone', 'owner_name', 'name', 'region', 'city', 'address', 
            'latitude', 'longitude', 'phone', 'phone2', 'description', 
            'profile_photo', 'working_hours_from', 'working_hours_to', 
            'is_active', 'created_at', 'calculated_distance_km', 'seats_count'
        ]
        extra_kwargs = {
            'owner': {'read_only': True},
            'latitude': {'required': True},
            'longitude': {'required': True},
        }

    def get_seats_count(self, obj):
        return obj.seats.count()

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude -90 va 90 oralig'ida bo'lishi kerak.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude -180 va 180 oralig'ida bo'lishi kerak.")
        return value


class TypeSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type_Seat
        fields = ['id', 'club', 'type_title']


class TypeRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type_Room
        fields = ['id', 'club', 'type_title']


class SeatSerializer(serializers.ModelSerializer):
    type_seat_title = serializers.ReadOnlyField(source='type_seat.type_title')
    type_room_title = serializers.ReadOnlyField(source='type_room.type_title')
    club_name = serializers.ReadOnlyField(source='club.name')

    class Meta:
        model = Seat
        fields = [
            'id', 'club', 'club_name', 'name', 'type_seat', 'type_seat_title',
            'type_room', 'type_room_title', 'hourly_price', 'is_booked', 'is_active'
        ]


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'payment']


class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.full_name')
    user_phone = serializers.ReadOnlyField(source='user.phone_number')
    seat_name = serializers.ReadOnlyField(source='seat.name')
    club_name = serializers.ReadOnlyField(source='seat.club.name')
    club_id = serializers.ReadOnlyField(source='seat.club.id')
    hall = serializers.ReadOnlyField(source='seat.type_room.type_title')

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_name', 'user_phone', 'seat', 'seat_name',
            'club_id', 'club_name', 'hall', 'date', 'start_time', 'end_time',
            'status', 'payment_method', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
