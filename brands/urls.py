from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    BrandProfileViewSet,
    ProductViewSet,
    ProductImageViewSet,
    ProductVideoViewSet,
    PublicProductListView,
    ProductByBrandView,
    ProductByCategoryView,
    PublicBrandListView,
    PublicBrandDetailView,
    BrandsByCategoryView,
    PublicProductDetailView,
    LatestProductsByCountView,
)

router = DefaultRouter()
router.register(r'profile',        BrandProfileViewSet,  basename='brand-profile')
router.register(r'products',       ProductViewSet,       basename='products')
router.register(r'product-images', ProductImageViewSet,  basename='product-images')
router.register(r'product-videos', ProductVideoViewSet,  basename='product-videos')

urlpatterns = router.urls

urlpatterns += [
    path('public/products/', PublicProductListView.as_view(), name='public-products'),
    path('public/products/<int:id>/', PublicProductDetailView.as_view(), name='public-product-detail'),
    path('public/products/brand/<int:brand_id>/', ProductByBrandView.as_view(), name='products-by-brand'),
    path('public/products/category/<str:category>/', ProductByCategoryView.as_view(), name='products-by-category'),
    path('public/products/latest/<int:count>/', LatestProductsByCountView.as_view(), name='latest-products-by-count'),

    path('public/brands/', PublicBrandListView.as_view(), name='public-brands'),
    path('public/brands/<int:id>/', PublicBrandDetailView.as_view(), name='brand-detail'),
    path('public/brands/category/<str:category>/', BrandsByCategoryView.as_view(), name='brands-by-category'),
]
