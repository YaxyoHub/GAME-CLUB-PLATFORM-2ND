from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    LoginSerializer, 
    LogoutSerializer, 
    RegisterSerializer,
    TelegramBotAuthSerializer,
    UserUpdateSerializer,
    UserListSerializer
)

User = get_user_model()

# =======================================
#        AUTHENTICATION & USER VIEWS
# =======================================

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'detail': "Muvaffaqiyatli ro'yxatdan o'tdingiz.",
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'phone_number': user.phone_number,
                'full_name': user.full_name,
                'role': user.role,
            }
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'phone_number': user.phone_number,
                'full_name': user.full_name,
                'role': user.role,
            }
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist() 

            return Response(
                {"detail": "Tizimdan muvaffaqiyatli chiqdingiz."}, 
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError:
            return Response(
                {"detail": "Yaroqsiz yoki allaqachon ishlatilgan token!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(APIView):
    """
    Foydalanuvchi profil ma'lumotlarini ko'rish (GET) 
    va tahrirlash/yangilash (PATCH / PUT) uchun API.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Profil ma'lumotlarini olish"""
        serializer = UserListSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Profil ma'lumotlarini qisman yangilash"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'detail': "Profil ma'lumotlari muvaffaqiyatli yangilandi.",
            'user': UserListSerializer(request.user).data
        }, status=status.HTTP_200_OK)

    def put(self, request):
        return self.patch(request)

# Orqaga moslik uchun
EditAccountAPIView = UserProfileView


class AdminUserListView(APIView):
    """
    Superadmin uchun barcha foydalanuvchilar ro'yxatini olish API.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'superadmin' and not request.user.is_superuser:
            return Response({"detail": "Faqat superadmin foydalanuvchilar ro'yxatini ko'rishi mumkin."}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.all().order_by('-date_joined')
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUserRoleUpdateView(APIView):
    """
    Superadmin uchun foydalanuvchi rolini o'zgartirish API.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != 'superadmin' and not request.user.is_superuser:
            return Response({"detail": "Faqat superadmin rolni o'zgartirishi mumkin."}, status=status.HTTP_403_FORBIDDEN)

        target_user = get_object_or_404(User, pk=pk)
        new_role = request.data.get('role')

        allowed_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if new_role not in allowed_roles:
            return Response(
                {"detail": f"Noto'g'ri rol! Ruxsat etilgan rollar: {', '.join(allowed_roles)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        target_user.role = new_role
        # Agar superadmin qilinsa, is_staff ham berilishi mumkin
        if new_role == 'superadmin':
            target_user.is_staff = True
        target_user.save()

        return Response({
            'detail': f"{target_user.phone_number} foydalanuvchi roli '{new_role}' ga muvaffaqiyatli o'zgartirildi.",
            'id': target_user.id,
            'role': target_user.role,
            'phone_number': target_user.phone_number,
            'full_name': target_user.full_name
        }, status=status.HTTP_200_OK)


class AdminUserToggleActiveView(APIView):
    """
    Superadmin uchun foydalanuvchini bloklash / faollashtirish API.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != 'superadmin' and not request.user.is_superuser:
            return Response({"detail": "Faqat superadmin bajara oladi."}, status=status.HTTP_403_FORBIDDEN)
        
        target_user = get_object_or_404(User, pk=pk)
        target_user.is_active = not target_user.is_active
        target_user.save()

        return Response({
            "detail": f"{target_user.phone_number} holati {'faollashtirildi' if target_user.is_active else 'bloklandi'}.",
            "id": target_user.id,
            "is_active": target_user.is_active
        }, status=status.HTTP_200_OK)


class AdminUserDeleteView(APIView):
    """
    Superadmin uchun foydalanuvchini tizimdan o'chirish API.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        if request.user.role != 'superadmin' and not request.user.is_superuser:
            return Response({"detail": "Faqat superadmin bajara oladi."}, status=status.HTTP_403_FORBIDDEN)
        
        target_user = get_object_or_404(User, pk=pk)
        if target_user == request.user:
            return Response({"detail": "O'z hisobingizni bu yerdan o'chira olmaysiz."}, status=status.HTTP_400_BAD_REQUEST)
        
        target_user.delete()
        return Response({"detail": "Foydalanuvchi muvaffaqiyatli o'chirildi."}, status=status.HTTP_200_OK)


class DeleteAccountAPIView(APIView):
    """
    Foydalanuvchi hisobini va (ixtiyoriy) uning refresh tokenini
    bekor qilib, hisobni tizimdan o'chiradi.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        user.delete()

        return Response(
            {"detail": "Hisobingiz muvaffaqiyatli o'chirildi."}, 
            status=status.HTTP_200_OK
        )


# =======================================
#           TELEGRAM BOT VIEWS
# =======================================

class TelegramBotAuthAPIView(APIView):
    """
    Telegram bot orqali kirish/ro'yxatdan o'tish uchun API.
    Bot foydalanuvchining telegram_chat_id va telefon raqamini yuboradi.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TelegramBotAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'status': 'success',
            'detail': "Bot orqali muvaffaqiyatli autentifikatsiya qilindingiz.",
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'phone_number': user.phone_number,
                'full_name': user.full_name,
                'address': getattr(user, 'address', ''),
                'telegram_chat_id': getattr(user, 'telegram_chat_id', None),
                'role': user.role,
            }
        }, status=status.HTTP_200_OK)