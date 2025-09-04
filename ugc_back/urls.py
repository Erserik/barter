from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="UGC Backend API",
        default_version='v1',
        description="Регистрация менеджеров, брендов, блогеров + JWT + Swagger",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # user API
    path('api/user/', include('accounts.urls')),
    path('api/brands/', include('brands.urls')),
    path('api/bloggers/', include('bloggers.urls')),


    # Swagger / ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('redoc/',  schema_view.with_ui('redoc',  cache_timeout=0), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
