from math import radians, cos, sin, asin, sqrt
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Club
from .serializers import ClubSerializer

# 1. SEE ALL CLUBS (Barcha klublarni ko'rish)
class ClubListView(generics.ListAPIView):
    queryset = Club.objects.filter(is_active=True)
    serializer_class = ClubSerializer
    permission_classes = [permissions.AllowAny]


# 2. CREATE CLUB (Klub yaratish)
class ClubCreateView(generics.CreateAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # So'rov yuborgan foydalanuvchini avtomatik owner (ega) qilib saqlaydi
        serializer.save(owner=self.request.user)


# 3. UPDATE CLUB BY MANAGER/OWNER (Klub egasi tomonidan tahrirlash)
class IsClubOwner(permissions.BasePermission):
    """Klubni faqat uning haqiqiy egasi (owner) tahrirlay olishi uchun cheklov"""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class ClubUpdateByManagerView(generics.UpdateAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAuthenticated, IsClubOwner]
    lookup_field = 'pk'  # UUID orqali qidiradi


# 4. UPDATE CLUB BY SUPERADMIN (Superadmin tomonidan tahrirlash)
class ClubUpdateBySuperAdminView(generics.UpdateAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAdminUser]  # is_staff=True yoki is_superuser=True
    lookup_field = 'pk'


# 5. DELETE CLUB (Klubni o'chirish)
class ClubDeleteView(generics.DestroyAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'


# 6. SEE CLUB BY CITY (Shahar bo'yicha klublarni ko'rish)
class ClubByCityView(generics.ListAPIView):
    serializer_class = ClubSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        city_name = self.kwargs.get('city')
        # Katta-kichik harflarni farqlamay shahar bo'yicha filtrlaydi
        return Club.objects.filter(city__icontains=city_name, is_active=True)


# 7. SEE CLUB BY LAT LONG (Koordinata va masofa bo'yicha JSON orqali qidirish)
class ClubByLocationView(generics.GenericAPIView):
    serializer_class = ClubSerializer
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

        # Haversine matematik formulasi
        for club in clubs:
            if club.latitude is None or club.longitude is None:
                continue
            
            lat2 = float(club.latitude)
            lon2 = float(club.longitude)

            # Graduslarni radianga o'tkazish
            lon1_r, lat1_r, lon2_r, lat2_r = map(radians, [lon1, lat1, lon2, lat2])

            dlon = lon2_r - lon1_r
            dlat = lat2_r - lat1_r
            a = sin(dlat/2)**2 + cos(lat1_r) * cos(lat2_r) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6371 * c  # Er yuzi radiusi o'rtacha 6371 km

            if km <= max_distance:
                serializer = self.get_serializer(club)
                club_data = serializer.data
                club_data['calculated_distance_km'] = round(km, 2)
                nearby_clubs.append(club_data)

        # Eng yaqin masofadan uzoq masofaga qarab saralash
        nearby_clubs.sort(key=lambda x: x['calculated_distance_km'])

        return Response(nearby_clubs, status=status.HTTP_200_OK)
