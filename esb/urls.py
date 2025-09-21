from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import ESBGatewayView

schema_view_esb = get_schema_view(
    openapi.Info(
        title="ESB API",
        default_version="v1",
        description="Документация только для ESB Gateway",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("gateway/", ESBGatewayView.as_view(), name="esb-gateway"),

    # Swagger только для ESB
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view_esb.without_ui(cache_timeout=0), name='schema-json-esb'),
    path('swagger/', schema_view_esb.with_ui('swagger', cache_timeout=0), name='schema-swagger-esb'),
    path('redoc/', schema_view_esb.with_ui('redoc', cache_timeout=0), name='schema-redoc-esb'),
]
