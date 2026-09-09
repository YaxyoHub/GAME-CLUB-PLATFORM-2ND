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
    UserUpdateSerializer  # <- Yangi serializer qo'shildi
)

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


class EditAccountAPIView(APIView):
    """
    Foydalanuvchi profil ma'lumotlarini ko'rish (GET) 
    va tahrirlash/yangilash (PATCH / PUT) uchun API.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Profil ma'lumotlarini olish"""
        serializer = UserUpdateSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Profil ma'lumotlarini qisman yangilash"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'detail': "Profil ma'lumotlari muvaffaqiyatli yangilandi.",
            'user': serializer.data
        }, status=status.HTTP_200_OK)


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