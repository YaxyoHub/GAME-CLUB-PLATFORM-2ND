from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import LoginSerializer, LogoutSerializer

# =======================================
#         LOGIN, LOGOUT, DELETE
# =======================================

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # SimpleJWT orqali token generatsiya qilish
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

# ----------------------------------------->

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

# ----------------------------------------->

class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user

        user.delete()

        return Response(
            {"detail": "Hisobingiz muvaffaqiyatli o'chirildi."}, 
            status=status.HTTP_204_NO_CONTENT
        )