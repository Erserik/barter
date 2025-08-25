from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import ManagerProfile, BrandProfile, BloggerProfile
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from rest_framework.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

User = get_user_model()


class ManagerRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.HiddenField(default='manager')
    full_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'phone', 'password', 'role', 'full_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        full_name = validated_data.pop('full_name')
        user = User.objects.create_user(**validated_data)
        ManagerProfile.objects.create(user=user, full_name=full_name)
        return user


class BrandRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.HiddenField(default='brand')
    full_name = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True, required=False, default='')
    logo = serializers.ImageField(write_only=True, required=False, default=None)
    city = serializers.CharField(write_only=True)
    category = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'phone', 'password', 'role', 'full_name',
            'company_name', 'description', 'logo', 'city', 'category',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        validated_data['username'] = validated_data['email']

        profile_data = {
            k: validated_data.pop(k)
            for k in ('company_name', 'description', 'logo', 'city', 'category')
        }

        user = User.objects.create_user(**validated_data)
        BrandProfile.objects.create(user=user, full_name=full_name, **profile_data)
        return user


class BloggerRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.HiddenField(default='blogger')
    full_name = serializers.CharField(write_only=True)
    city = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(
        choices=BloggerProfile.GENDER_CHOICES,
        write_only=True
    )
    instagram = serializers.URLField(write_only=True, required=False, default='')
    tiktok = serializers.URLField(write_only=True, required=False, default='')
    youtube = serializers.URLField(write_only=True, required=False, default='')
    birth_date = serializers.DateField(write_only=True, required=False, allow_null=True)  # ✅
    avatar = serializers.ImageField(write_only=True, required=False)
    description = serializers.CharField(write_only=True, required=False, allow_blank=True)  # ✅ добавлено



    class Meta:
        model = User
        fields = (
            'email', 'phone', 'password', 'role',
            'full_name', 'avatar', 'city', 'gender',
            'instagram', 'tiktok', 'youtube', 'birth_date', 'description'  # ✅
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']

        instagram = validated_data.pop('instagram', '')
        tiktok = validated_data.pop('tiktok', '')
        youtube = validated_data.pop('youtube', '')
        birth_date = validated_data.pop('birth_date', None)
        avatar = validated_data.pop('avatar', None)  # ✅ извлекаем

        full_name = validated_data.pop('full_name')
        city = validated_data.pop('city')
        gender = validated_data.pop('gender')
        description = validated_data.pop('description')

        user = User.objects.create_user(**validated_data)

        BloggerProfile.objects.create(
            user=user,
            full_name=full_name,
            city=city,
            gender=gender,
            avatar=avatar,  # ✅ передаём
            instagram=instagram,
            tiktok=tiktok,
            youtube=youtube,
            birth_date=birth_date,
            description=description
        )

        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['role'] = user.role
        token['email'] = user.email
        token['user_id'] = user.id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # 👇 Эти поля будут в JSON-ответе при логине
        data['role'] = self.user.role
        data['email'] = self.user.email
        data['user_id'] = self.user.id

        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с такой почтой не найден.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = f"https://dev.tusapp.kz/reset-password/{uid}/{token}/"
        # Заменить на фронтовую ссылку в проде

        send_mail(
            subject="Восстановление пароля",
            message=f"Перейдите по ссылке для сброса пароля:\n{reset_link}",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

class SetNewPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            user = User.objects.get(pk=uid)
        except Exception:
            raise ValidationError("Неверная ссылка восстановления")

        if not PasswordResetTokenGenerator().check_token(user, data['token']):
            raise ValidationError("Ссылка недействительна или устарела")

        user.set_password(data['new_password'])
        user.save()
        return data