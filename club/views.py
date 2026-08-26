from math import radians, cos, sin, asin, sqrt
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Club
from .serializers import ClubSerializer


# 1. SEE ALL CLUBS
class ClubListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        clubs = Club.objects.filter(is_active=True)
        serializer = ClubSerializer(clubs, many=True)
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
        
        # Egalik huquqini tekshirish
        if club.owner != request.user:
            return Response(
                {"detail": "Sizda ushbu klubni tahrirlash huquqi yo'q."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = ClubSerializer(club, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        club = get_object_or_404(Club, pk=pk)
        
        if club.owner != request.user:
            return Response(
                {"detail": "Sizda ushbu klubni tahrirlash huquqi yo'q."},
                status=status.HTTP_403_FORBIDDEN
            )
            
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
        return Response(
            {"message": "Klub muvaffaqiyatli o'chirildi."},
            status=status.HTTP_204_NO_CONTENT
        )


# 6. SEE CLUB BY CITY
class ClubByCityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, city, *args, **kwargs):
        clubs = Club.objects.filter(city__icontains=city, is_active=True)
        serializer = ClubSerializer(clubs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 7. SEE CLUB BY LAT LONG
class ClubByLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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


            # GEOPY ORQALI QILINSIN
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