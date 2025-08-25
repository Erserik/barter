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