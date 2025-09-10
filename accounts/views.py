from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

from .serializers import (
    ManagerRegistrationSerializer,
    BrandRegistrationSerializer,
    BloggerRegistrationSerializer,
    MyTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    SetNewPasswordSerializer
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)  # создаёт refresh + access токены

    return {
        'refresh': str(refresh),                    # обычный refresh токен
        'access':  str(refresh.access_token),       # access токен
        'role': user.role,                          # роль пользователя
        'email': user.email,                        # email
        'user_id': user.id,                         # ID
    }


class ManagerRegisterView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ManagerRegistrationSerializer

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(get_tokens_for_user(user),
                        status=status.HTTP_201_CREATED)


class BrandRegisterView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = BrandRegistrationSerializer

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(get_tokens_for_user(user),
                        status=status.HTTP_201_CREATED)


class BloggerRegisterView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = BloggerRegistrationSerializer

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(get_tokens_for_user(user),
                        status=status.HTTP_201_CREATED)


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

class PasswordResetRequestView(APIView):
    @swagger_auto_schema(
        request_body=PasswordResetRequestSerializer,
        operation_summary="Запрос на сброс пароля",
        operation_description="Отправляет ссылку на сброс пароля на почту пользователя",
        responses={200: "Ссылка для сброса отправлена"},
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Ссылка для сброса отправлена на email'}, status=200)


class PasswordResetConfirmView(APIView):
    @swagger_auto_schema(
        request_body=SetNewPasswordSerializer,
        operation_summary="Подтверждение нового пароля",
        operation_description="Устанавливает новый пароль после перехода по ссылке из письма",
        responses={200: "Пароль успешно изменен"},
    )
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Пароль успешно изменен'}, status=200)

# apps/accounts/views.py (добавка)
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from .models import ManagerProfile, BrandProfile, BloggerProfile
from .serializers import GoogleAuthSerializer
# get_tokens_for_user у тебя уже объявлен выше в этом файле

User = get_user_model()

def _create_profile_if_needed(user, role, data):
    """Создаёт профиль один раз при первом входе через Google."""
    base_name = (data.get('full_name') or user.email.split('@')[0])

    if role == 'manager' and not hasattr(user, 'manager_profile'):
        ManagerProfile.objects.create(user=user, full_name=base_name)

    elif role == 'brand' and not hasattr(user, 'brand_profile'):
        BrandProfile.objects.create(
            user=user,
            full_name=base_name,
            company_name=data.get('company_name') or 'Company',
            description=data.get('description', ''),
            logo=None,
            city=data.get('city') or '',
            category=data.get('category') or ''
        )

    elif role == 'blogger' and not hasattr(user, 'blogger_profile'):
        BloggerProfile.objects.create(
            user=user,
            full_name=base_name,
            city=data.get('city') or '',
            gender=data.get('gender') or 'male',
            avatar=None,
            instagram=data.get('instagram', ''),
            tiktok=data.get('tiktok', ''),
            youtube=data.get('youtube', ''),
            birth_date=None,
            description=data.get('description', '')
        )


class GoogleAuthView(APIView):
    """
    POST /api/user/auth/google/
    Body: { "id_token": "<google_id_token>", ...optional profile fields... }
    """
    permission_classes = (permissions.AllowAny,)
    authentication_classes = []  # чтобы не словить CSRF от SessionAuth

    # если используешь drf_yasg — можешь обернуть swagger_auto_schema тут

    def post(self, request):
        ser = GoogleAuthSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        id_token_str = ser.validated_data['id_token']

        try:
            # 1) Проверка id_token у Google
            idinfo = google_id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request()
            )

            # 2) iss
            allowed_iss = getattr(settings, 'GOOGLE_ISSUERS', ["accounts.google.com", "https://accounts.google.com"])
            if idinfo.get('iss') not in allowed_iss:
                return Response({"detail": "Invalid token issuer"}, status=status.HTTP_400_BAD_REQUEST)

            # 3) aud (должен совпасть с твоим Client ID)
            allowed_aud = set(getattr(settings, 'GOOGLE_OAUTH2_CLIENT_IDS', []))
            if idinfo.get('aud') not in allowed_aud:
                return Response({"detail": "Wrong audience"}, status=status.HTTP_400_BAD_REQUEST)

            # 4) email
            email = idinfo.get('email')
            if not email:
                return Response({"detail": "Email not present in token"}, status=status.HTTP_400_BAD_REQUEST)

            if not idinfo.get('email_verified', False):
                return Response({"detail": "Email not verified by Google"}, status=status.HTTP_400_BAD_REQUEST)

            # 5) Находим/создаём пользователя
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,   # для AbstractUser
                    "is_confirmed": True
                }
            )

            wanted_role = ser.validated_data.get('role')

            if created:
                # Если это первый вход — выставляем роль (если пришла), иначе по умолчанию 'blogger'
                user.role = wanted_role or 'blogger'
                user.save(update_fields=['role'])
                _create_profile_if_needed(user, user.role, ser.validated_data)
            else:
                # Роль существующему пользователю НЕ меняем (чтобы не сломать доступ)
                # Если хочешь — можно возвращать 409 при попытке смены:
                # if wanted_role and user.role and user.role != wanted_role:
                #     return Response({"detail": "Role change is not allowed"}, status=status.HTTP_409_CONFLICT)
                pass

            # 6) Выдаём твои JWT
            tokens = get_tokens_for_user(user)
            return Response(tokens, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"detail": "Invalid Google id_token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
