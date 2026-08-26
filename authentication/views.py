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
    TelegramBotAuthSerializer
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

        # Ro'yxatdan o'tgandan so'ng avtomatik JWT token generatsiya qilish
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
            token.blacklist()  # Tokenni qora ro'yxatga kiritadi

            return Response(
                {"detail": "Tizimdan muvaffaqiyatli chiqdingiz."}, 
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError:
            return Response(
                {"detail": "Yaroqsiz yoki allaqachon ishlatilgan token!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class DeleteAccountAPIView(APIView):
    """
    Foydalanuvchi hisobini va (ixtiyoriy) uning refresh tokenini
    bekor qilib, hisobni tizimdan o'chiradi.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        
        # Agar so'rovda refresh token berilgan bo'lsa, uni blacklist qilamiz
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        # Foydalanuvchini o'chirish
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
    Bot foydalanuvchining telegram_id va telefon raqamini yuboradi.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TelegramBotAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'detail': "Bot orqali muvaffaqiyatli autentifikatsiya qilindingiz.",
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'phone_number': user.phone_number,
                'full_name': user.full_name,
                'telegram_id': getattr(user, 'telegram_id', None),
                'role': user.role,
            }
        }, status=status.HTTP_200_OK)

class TelegramBotAuthAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TelegramBotAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        # DRF orqali JWT token va foydalanuvchi ma'lumotlarini qaytarish
        return Response({
            'status': 'success',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'phone_number': user.phone_number,
                'full_name': user.full_name,
                'address': getattr(user, 'address', ''),
                'telegram_id': user.telegram_id,
            }
        }, status=status.HTTP_200_OK)

