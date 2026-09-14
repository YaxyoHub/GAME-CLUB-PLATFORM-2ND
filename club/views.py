from math import radians, cos, sin, asin, sqrt
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Club, Seat, Type_Seat, Type_Room, Booking, Card
from .serializers import ClubSerializer, SeatSerializer, BookingSerializer


# 1. SEE ALL CLUBS (Ommaviy - barcha uchun ochiq)
class ClubListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        clubs = Club.objects.filter(is_active=True)
        serializer = ClubSerializer(clubs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 1.1 SINGLE CLUB DETAIL
class ClubDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        club = get_object_or_404(Club, pk=pk)
        serializer = ClubSerializer(club)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 2. CREATE CLUB
class ClubCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ClubSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 3. UPDATE CLUB BY MANAGER/OWNER
class ClubUpdateByManagerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        club = get_object_or_404(Club, pk=pk)
        if club.owner != request.user and request.user.role != 'superadmin':
            return Response({"detail": "Sizda ushbu klubni tahrirlash huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = ClubSerializer(club, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        club = get_object_or_404(Club, pk=pk)
        if club.owner != request.user and request.user.role != 'superadmin':
            return Response({"detail": "Sizda ushbu klubni tahrirlash huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = ClubSerializer(club, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 4. UPDATE CLUB BY SUPERADMIN
class ClubUpdateBySuperAdminView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, pk, *args, **kwargs):
        club = get_object_or_404(Club, pk=pk)
        serializer = ClubSerializer(club, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        club = get_object_or_404(Club, pk=pk)
        serializer = ClubSerializer(club, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 5. DELETE CLUB
class ClubDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk, *args, **kwargs):
        club = get_object_or_404(Club, pk=pk)
        club.delete()
        return Response({"message": "Klub muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)


# 6. SEE CLUB BY CITY
class ClubByCityView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, city, *args, **kwargs):
        clubs = Club.objects.filter(city__icontains=city, is_active=True)
        serializer = ClubSerializer(clubs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 7. SEE CLUB BY LAT LONG
class ClubByLocationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        lat1 = request.data.get('lat')
        lon1 = request.data.get('long')
        max_distance = request.data.get('distance')

        if lat1 is None or lon1 is None or max_distance is None:
            raise ValidationError({"error": "Siz 'lat', 'long' va 'distance' qiymatlarini yuborishingiz shart."})

        try:
            lat1 = float(lat1)
            lon1 = float(lon1)
            max_distance = float(max_distance)
        except ValueError:
            raise ValidationError({"error": "Lat, long va distance haqiqiy raqam bo'lishi kerak."})

        clubs = Club.objects.filter(is_active=True)
        nearby_clubs = []

        for club in clubs:
            if club.latitude is None or club.longitude is None:
                continue
            
            lat2 = float(club.latitude)
            lon2 = float(club.longitude)

            lon1_r, lat1_r, lon2_r, lat2_r = map(radians, [lon1, lat1, lon2, lat2])

            dlon = lon2_r - lon1_r
            dlat = lat2_r - lat1_r
            a = sin(dlat/2)**2 + cos(lat1_r) * cos(lat2_r) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6371 * c

            if km <= max_distance:
                serializer = ClubSerializer(club)
                club_data = serializer.data
                club_data['calculated_distance_km'] = round(km, 2)
                nearby_clubs.append(club_data)

        nearby_clubs.sort(key=lambda x: x['calculated_distance_km'])
        return Response(nearby_clubs, status=status.HTTP_200_OK)


# ==========================================
#        SEATS (KOMPYUTERLAR) VIEWS
# ==========================================

class ClubSeatsView(APIView):
    """
    Klubdagi 30 ta kompyuterni olish.
    Agar klubda hali kompyuterlar yaratilmagan bo'lsa, avtomatik 30 ta kompyuter hosil qiladi.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        club = get_object_or_404(Club, pk=pk)
        seats = Seat.objects.filter(club=club).order_by('name')

        # Agar bazada kompyuterlar bo'lmasa, avtomatik 30 ta kompyuterni generatsiya qilamiz
        if not seats.exists():
            vip_room, _ = Type_Room.objects.get_or_create(club=club, type_title="VIP Zal")
            standart_room, _ = Type_Room.objects.get_or_create(club=club, type_title="Umumiy Zal")
            bootcamp_room, _ = Type_Room.objects.get_or_create(club=club, type_title="Bootcamp")
            ps_room, _ = Type_Room.objects.get_or_create(club=club, type_title="PlayStation")

            vip_seat, _ = Type_Seat.objects.get_or_create(club=club, type_title="VIP")
            standart_seat, _ = Type_Seat.objects.get_or_create(club=club, type_title="Standart")
            pro_seat, _ = Type_Seat.objects.get_or_create(club=club, type_title="Pro Gaming")
            ps_seat, _ = Type_Seat.objects.get_or_create(club=club, type_title="PS5")

            new_seats = []
            # 1-6 VIP
            for i in range(1, 7):
                new_seats.append(Seat(
                    club=club, name=f"PC #{i:02d}", type_seat=vip_seat, type_room=vip_room, hourly_price=25000
                ))
            # 7-20 Standart
            for i in range(7, 21):
                new_seats.append(Seat(
                    club=club, name=f"PC #{i:02d}", type_seat=standart_seat, type_room=standart_room, hourly_price=12000
                ))
            # 21-25 Bootcamp
            for i in range(21, 26):
                new_seats.append(Seat(
                    club=club, name=f"PC #{i:02d}", type_seat=pro_seat, type_room=bootcamp_room, hourly_price=18000
                ))
            # 26-30 PlayStation
            for i in range(26, 31):
                new_seats.append(Seat(
                    club=club, name=f"PS5 #{i-25:02d}", type_seat=ps_seat, type_room=ps_room, hourly_price=20000
                ))

            Seat.objects.bulk_create(new_seats)
            seats = Seat.objects.filter(club=club).order_by('name')

        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SeatReleaseView(APIView):
    """
    O'rindiqni bo'shatish (Menejer yoki Superadmin)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        seat = get_object_or_404(Seat, pk=pk)
        
        # Tekshirish: klub egasimi yoki superadminmi
        if seat.club.owner != request.user and request.user.role != 'superadmin' and not request.user.is_superuser:
            return Response({"detail": "Sizda bu o'rindiqni bo'shatish huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)

        seat.is_booked = False
        seat.save()

        # O'rindiqdagi aktiv bronlarni yakunlash
        Booking.objects.filter(seat=seat, status__in=[Booking.Status.BOOKED, Booking.Status.PLAYING]).update(
            status=Booking.Status.FINISHED
        )

        return Response({"message": f"{seat.name} muvaffaqiyatli bo'shatildi.", "is_booked": False}, status=status.HTTP_200_OK)


class SeatOccupyView(APIView):
    """
    O'rindiqni band qilish (Menejer yoki Superadmin)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        seat = get_object_or_404(Seat, pk=pk)
        
        if seat.club.owner != request.user and request.user.role != 'superadmin' and not request.user.is_superuser:
            return Response({"detail": "Sizda bu o'rindiqni band qilish huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)

        seat.is_booked = True
        seat.save()

        return Response({"message": f"{seat.name} band qilindi.", "is_booked": True}, status=status.HTTP_200_OK)


# ==========================================
#        BOOKING (BRON QILISH) VIEWS
# ==========================================

class BookingCreateView(APIView):
    """
    Kompyuterni bron qilish
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        seat_id = request.data.get('seat_id')
        date_str = request.data.get('date', timezone.now().strftime('%Y-%m-%d'))
        start_time_str = request.data.get('start_time', timezone.now().strftime('%H:%M:%S'))
        end_time_str = request.data.get('end_time', None)
        payment_type = request.data.get('payment_method', 'card')

        if not seat_id:
            return Response({"detail": "O'rindiq (seat_id) tanlanishi shart!"}, status=status.HTTP_400_BAD_REQUEST)

        seat = get_object_or_404(Seat, pk=seat_id)
        if seat.is_booked:
            return Response({"detail": "Kechirasiz, ushbu kompyuter allaqachon band qilingan!"}, status=status.HTTP_400_BAD_REQUEST)

        card = Card.objects.filter(payment__icontains=payment_type).first()
        if not card:
            card, _ = Card.objects.get_or_create(payment=payment_type)

        booking = Booking.objects.create(
            user=request.user,
            seat=seat,
            date=date_str,
            start_time=start_time_str,
            end_time=end_time_str if end_time_str else None,
            status=Booking.Status.BOOKED,
            payment_method=card
        )

        # Kompyuterni band holatga o'tkazish
        seat.is_booked = True
        seat.save()

        serializer = BookingSerializer(booking)
        return Response({
            "message": "Kompyuter muvaffaqiyatli band qilindi!",
            "booking": serializer.data
        }, status=status.HTTP_201_CREATED)


class UserBookingsView(APIView):
    """
    Mijozning o'z bronlarini ko'rish
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingCancelView(APIView):
    """
    Bronni bekor qilish. Bekor qilinganda o'rindiq darhol bo'shatiladi!
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)

        # Foydalanuvchi o'z bronini, klub egasi yoki superadmin bekor qila oladi
        is_owner = booking.user == request.user
        is_club_manager = booking.seat.club.owner == request.user
        is_admin = request.user.role == 'superadmin' or request.user.is_superuser

        if not (is_owner or is_club_manager or is_admin):
            return Response({"detail": "Sizda ushbu bronni bekor qilish huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)

        booking.status = Booking.Status.FINISHED
        booking.save()

        # Kompyuterni darhol bo'shatish
        seat = booking.seat
        seat.is_booked = False
        seat.save()

        return Response({
            "message": "Bron muvaffaqiyatli bekor qilindi va kompyuter bo'shatildi.",
            "seat_id": str(seat.id),
            "is_booked": False
        }, status=status.HTTP_200_OK)


class AllBookingsView(APIView):
    """
    Barcha bronlar ro'yxati (Klub menejeri yoki Superadmin uchun)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == 'superadmin' or request.user.is_superuser:
            bookings = Booking.objects.all().order_by('-created_at')
        elif request.user.role == 'club manager':
            bookings = Booking.objects.filter(seat__club__owner=request.user).order_by('-created_at')
        else:
            return Response({"detail": "Ruxsat berilmagan."}, status=status.HTTP_403_FORBIDDEN)

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)