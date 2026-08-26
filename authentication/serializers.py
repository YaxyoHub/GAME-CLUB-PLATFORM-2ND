from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
import re

User = get_user_model()

# ========================================
#        LOGIN, LOGOUT, REGISTER & BOT
# ========================================

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'full_name', 'role', 'password', 'password_confirm']

    def validate_phone_number(self, value):

        pattern = r"^\+998\d{9}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError("Telefon raqami +998901234567 formatida bo'lishi kerak!")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Bu telefon raqami allaqachon ro'yxatdan o'tgan!")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Parollar bir-biriga mos kelmadi!"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(password=password, **validated_data)
        return user


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
    refresh = serializers.CharField(error_messages={'required': "Refresh token kiritilishi shart!"})


class TelegramBotAuthSerializer(serializers.Serializer):
    telegram_id = serializers.BigIntegerField()
    phone_number = serializers.CharField(max_length=13, required=False, allow_blank=True)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        telegram_id = attrs.get('telegram_id')
        phone_number = attrs.get('phone_number')
        full_name = attrs.get('full_name', 'Telegram User')

        user = User.objects.filter(telegram_id=telegram_id).first()

        if not user and phone_number:
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                user.telegram_id = telegram_id
                user.save()

        if not user:
            if not phone_number:
                raise serializers.ValidationError("Yangi foydalanuvchi yaratish uchun telefon raqami shart!")
            
            user = User.objects.create_user(
                phone_number=phone_number,
                telegram_id=telegram_id,
                full_name=full_name
            )

        if not user.is_active:
            raise serializers.ValidationError("Foydalanuvchi hisobi faol emas!")

        attrs['user'] = user
        return attrs
    
from rest_framework import serializers
from django.contrib.auth import get_user_model
import re

User = get_user_model()

class TelegramBotAuthSerializer(serializers.Serializer):
    telegram_id = serializers.BigIntegerField()
    phone_number = serializers.CharField(max_length=13, required=False, allow_blank=True)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        telegram_id = attrs.get('telegram_id')
        phone_number = attrs.get('phone_number')
        full_name = attrs.get('full_name')
        address = attrs.get('address')

        user = User.objects.filter(telegram_id=telegram_id).first()

        if not user and phone_number:
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                user.telegram_id = telegram_id
                user.save()

        if not user:
            if not phone_number:
                raise serializers.ValidationError({"detail": "Yangi foydalanuvchi uchun telefon raqam shart!"})
            
            user = User.objects.create_user(
                phone_number=phone_number,
                telegram_id=telegram_id,
                full_name=full_name or "Telegram User",
                address=address or ""
            )

        if not user.is_active:
            raise serializers.ValidationError({"detail": "Foydalanuvchi faol emas!"})

        attrs['user'] = user
        return attrs
    
