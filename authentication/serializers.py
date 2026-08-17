from rest_framework import serializers
from django.contrib.auth import authenticate


# ========================================
#      LOGIN, LOGOUT, DELETE
# ========================================

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        if phone_number and password:
            user = authenticate(
                request=self.context.get('request'),
                username=phone_number,
                password=password
            )

            if not user:
                raise serializers.ValidationError("Telefon raqami yoki parol noto'g'ri!")
            if not user.is_active:
                raise serializers.ValidationError("Hisobingiz faol emas!")
        else:
            raise serializers.ValidationError("Telefon raqam va parol kiritilishi shart!")

        attrs['user'] = user
        return attrs
    


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()