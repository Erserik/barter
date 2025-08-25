from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ManagerRegisterView,
    BrandRegisterView,
    BloggerRegisterView,
    MyTokenObtainPairView,
    PasswordResetRequestView,
    PasswordResetConfirmView
)

urlpatterns = [
    # регистрация
    path('register/manager/', ManagerRegisterView.as_view(), name='reg-manager'),
    path('register/brand/',   BrandRegisterView.as_view(),   name='reg-brand'),
    path('register/blogger/', BloggerRegisterView.as_view(), name='reg-blogger'),

    # логин по email → JWT
    path('login/',          MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/',  TokenRefreshView.as_view(),      name='token_refresh'),

    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

]
