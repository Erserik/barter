from django.contrib import admin
from .models import Product, ProductImage, ProductVideo


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('alt',)


@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'title', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title',)
