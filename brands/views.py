import json
from django.db import transaction
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Product, ProductImage, ProductVideo
from .serializers import (
    BrandProfileSerializer,
    ProductSerializer,
    PublicProductSerializer,
    PublicBrandSerializer,
    ProductImageSerializer,
    ProductVideoSerializer,
)
from accounts.models import BrandProfile
from .permissions import IsBrand  # если вынесли в отдельный файл, иначе оставьте локальный класс

class BrandProfileViewSet(viewsets.ModelViewSet):
    serializer_class = BrandProfileSerializer
    permission_classes = [IsBrand]

    def get_queryset(self):
        return BrandProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return BrandProfile.objects.get(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsBrand]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return Product.objects.filter(brand=self.request.user)

    def _extract_video_categories(self, data):
        vc = []
        if hasattr(data, 'getlist'):
            vc = data.getlist('video_categories[]') or data.getlist('video_categories')
        if not vc:
            raw = data.get('video_categories')
            if isinstance(raw, str) and raw.strip():
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        vc = parsed
                except json.JSONDecodeError:
                    pass
        return vc

    def perform_create(self, serializer):
        vc = self._extract_video_categories(self.request.data)
        serializer.save(brand=self.request.user, video_categories=vc)

    def perform_update(self, serializer):
        vc = self._extract_video_categories(self.request.data)
        if vc:
            serializer.save(video_categories=vc)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_media(self, request, pk=None):
        product = self.get_object()

        images = request.FILES.getlist('images')
        videos = request.FILES.getlist('videos')

        order_images = request.data.getlist('order_images') if hasattr(request.data, 'getlist') else []
        order_videos = request.data.getlist('order_videos') if hasattr(request.data, 'getlist') else []

        created_images, created_videos = [], []

        with transaction.atomic():
            for idx, f in enumerate(images):
                order = int(order_images[idx]) if idx < len(order_images) and str(order_images[idx]).isdigit() else 0
                created_images.append(
                    ProductImage.objects.create(product=product, file=f, order=order)
                )

            for idx, f in enumerate(videos):
                order = int(order_videos[idx]) if idx < len(order_videos) and str(order_videos[idx]).isdigit() else 0
                created_videos.append(
                    ProductVideo.objects.create(product=product, file=f, order=order)
                )

        return Response({
            "images": ProductImageSerializer(created_images, many=True).data,
            "videos": ProductVideoSerializer(created_videos, many=True).data
        })

    def _get_json_list(self, data, key):
        val = data.get(key, [])
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            s = val.strip()
            if not s:
                return []
            try:
                parsed = json.loads(s)
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                return []
        return []

    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        product = self.get_object()

        images = self._get_json_list(request.data, 'images')
        videos = self._get_json_list(request.data, 'videos')

        def ok(item): return isinstance(item, dict) and 'id' in item
        images = [i for i in images if ok(i)]
        videos = [v for v in videos if ok(v)]

        with transaction.atomic():
            for item in images:
                try:
                    obj = ProductImage.objects.get(id=item['id'], product=product)
                    obj.order = int(item.get('order', 0))
                    obj.save(update_fields=['order'])
                except ProductImage.DoesNotExist:
                    pass

            for item in videos:
                try:
                    obj = ProductVideo.objects.get(id=item['id'], product=product)
                    obj.order = int(item.get('order', 0))
                    obj.save(update_fields=['order'])
                except ProductVideo.DoesNotExist:
                    pass

        return Response({"detail": "Reordered"}, status=status.HTTP_200_OK)


class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsBrand]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return ProductImage.objects.filter(product__brand=self.request.user)


class ProductVideoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVideoSerializer
    permission_classes = [IsBrand]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return ProductVideo.objects.filter(product__brand=self.request.user)


# Публичные вьюхи (бренд+продукты)
class PublicProductListView(generics.ListAPIView):
    serializer_class = PublicProductSerializer
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny]


class ProductByBrandView(generics.ListAPIView):
    serializer_class = PublicProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        brand_id = self.kwargs.get("brand_id")
        return Product.objects.filter(brand__id=brand_id)


class ProductByCategoryView(generics.ListAPIView):
    serializer_class = PublicProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category = self.kwargs.get("category")
        return Product.objects.filter(category__iexact=category)


class PublicProductDetailView(generics.RetrieveAPIView):
    serializer_class = PublicProductSerializer
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'


class LatestProductsByCountView(generics.ListAPIView):
    serializer_class = PublicProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        count = int(self.kwargs.get('count', 4))
        return Product.objects.all().order_by('-id')[:count]


class PublicBrandListView(generics.ListAPIView):
    serializer_class = PublicBrandSerializer
    queryset = BrandProfile.objects.all()
    permission_classes = [permissions.AllowAny]


class PublicBrandDetailView(generics.RetrieveAPIView):
    serializer_class = PublicBrandSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        user_id = self.kwargs["id"]
        return BrandProfile.objects.get(user__id=user_id)


class BrandsByCategoryView(generics.ListAPIView):
    serializer_class = PublicBrandSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category = self.kwargs.get('category')
        return BrandProfile.objects.filter(category__iexact=category)
