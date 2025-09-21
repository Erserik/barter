from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from .adapters.geonames import get_cities_kz
from .adapters.country_info import get_country_info

class ESBGatewayView(APIView):
    @swagger_auto_schema(
        operation_summary="ESB Gateway",
        operation_description="Единая точка входа: выбери сервис (cities, country)",
        manual_parameters=[
            openapi.Parameter(
                'service',
                openapi.IN_QUERY,
                description="Выбор сервиса",
                type=openapi.TYPE_STRING,
                enum=["cities", "country"],
                required=True,
            ),
            openapi.Parameter(
                'code',
                openapi.IN_QUERY,
                description="ISO код страны (для service=country)",
                type=openapi.TYPE_STRING,
                default="KZ",
                required=False,
            ),
        ],
    )
    def get(self, request):
        service = request.query_params.get("service")

        if service == "cities":
            return Response(get_cities_kz())
        elif service == "country":
            code = request.query_params.get("code", "KZ")
            return Response(get_country_info(code))
        return Response({"status": "error", "detail": "Unknown service"}, status=400)
