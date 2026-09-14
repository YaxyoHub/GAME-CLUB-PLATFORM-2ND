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

from .models import User
from .serializers import UserSerializer

class TelegramBotAuthAPIView(APIView):
    """
    Telegram bot orqali kirish/ro'yxatdan o'tish uchun API.
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
                'telegram_chat_id': user.telegram_chat_id,
                'role': user.role,
            }
        }, status=status.HTTP_200_OK)


# =======================================
#           ADMIN & USER VIEWS
# =======================================

class AdminUserListView(APIView):
    """
    Faqat superadmin barcha foydalanuvchilarni ko'rishi mumkin
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'superadmin' and not request.user.is_superuser:
            return Response({"detail": "Sizda bu sahifaga kirish huquqi yo'q."}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.all().order_by('-id')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUserRoleUpdateView(APIView):
    """
    Faqat superadmin foydalanuvchi rolini o'zgartira oladi (client, club manager, superadmin)
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != 'superadmin' and not request.user.is_superuser:
            return Response({"detail": "Faqat superadmin rollarni o'zgartirishi mumkin!"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        new_role = request.data.get('role')
        if new_role not in ['client', 'club manager', 'superadmin']:
            return Response({"detail": "Noto'g'ri rol kiritildi."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.role = new_role
        if new_role == 'superadmin':
            target_user.is_staff = True
            target_user.is_superuser = True
        elif new_role == 'club manager':
            target_user.is_staff = True
            target_user.is_superuser = False
        else:
            target_user.is_staff = False
            target_user.is_superuser = False
            
        target_user.save()
        serializer = UserSerializer(target_user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    Joriy foydalanuvchi ma'lumotlarini olish va yangilash
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


