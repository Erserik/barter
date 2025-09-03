from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Product, ProductImage, ProductVideo
from accounts.models import BrandProfile

User = get_user_model()


class BrandProfileSerializer(serializers.ModelSerializer):
    is_confirmed = serializers.BooleanField(source='user.is_confirmed', read_only=True)
    created_at = serializers.DateTimeField(source='user.date_joined', read_only=True)

    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = BrandProfile
        fields = (
            'company_name',
            'full_name',
            'phone',
            'description',
            'logo',
            'city',
            'category',
            'is_confirmed',
            'created_at',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['phone'] = getattr(instance.user, 'phone', None)
        return data

    def update(self, instance, validated_data):
        phone = validated_data.pop('phone', None)
        if phone is not None:
            instance.user.phone = phone
            instance.user.save(update_fields=['phone'])
        return super().update(instance, validated_data)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'file', 'alt', 'order', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = ('id', 'file', 'title', 'order', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'image',
            'name',
            'description',
            'category',
            'video_categories',
            'created_at',
            'images',
            'videos',
        )
    # created_at read-only по умолчанию (auto_now_add)


class PublicProductSerializer(serializers.ModelSerializer):
    brand_id = serializers.IntegerField(source='brand.id', read_only=True)
    brand_name = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'brand_id',
            'brand_name',
            'image',
            'name',
            'description',
            'category',
            'created_at',
            'video_categories',
            'images',
            'videos',
        )

    def get_brand_name(self, obj):
        profile = getattr(obj.brand, 'brand_profile', None)
        return profile.company_name if profile else obj.brand.email


class PublicBrandSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='user.date_joined', read_only=True)
    is_confirmed = serializers.BooleanField(source='user.is_confirmed', read_only=True)

    class Meta:
        model = BrandProfile
        fields = ('user', 'company_name', 'description', 'logo', 'city', 'category', 'created_at', 'is_confirmed')
