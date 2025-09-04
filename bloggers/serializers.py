# bloggers/serializers.py

from rest_framework import serializers
from .models import UGCRequest, Favorite
from brands.serializers import PublicProductSerializer
from accounts.models import BloggerProfile
from brands.models import Invitation
from brands.serializers import PublicBrandSerializer

from brands.serializers import PublicProductSerializer

class InvitationSerializer(serializers.ModelSerializer):
    brand = serializers.SerializerMethodField()
    product = PublicProductSerializer(read_only=True)  # 👈 отображение информации о товаре

    class Meta:
        model = Invitation
        fields = ['id', 'brand', 'product', 'message', 'video_categories', 'status', 'created_at']
        read_only_fields = ['brand', 'message', 'created_at']

    def get_brand(self, obj):
        from accounts.models import BrandProfile
        try:
            profile = BrandProfile.objects.get(user=obj.brand)
            return PublicBrandSerializer(profile).data
        except BrandProfile.DoesNotExist:
            return None

class BloggerProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # это id BloggerProfile
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # это id из CustomUser
    is_confirmed = serializers.BooleanField(source='user.is_confirmed', read_only=True)  # ➕ добавлено


    class Meta:
        model = BloggerProfile
        fields = [
            'id',          # id самого BloggerProfile
            'user_id',     # id пользователя
            'full_name',
            'city',
            'avatar',
            'birth_date',
            'description',
            'gender',
            'instagram',
            'tiktok',
            'youtube',
            'is_confirmed',
        ]
class UGCRequestSerializer(serializers.ModelSerializer):
    product = PublicProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=UGCRequest._meta.get_field('product').related_model.objects.all(),
        write_only=True,
        source='product'
    )

    # 👇 Добавляем данные о блогере
    blogger_id = serializers.IntegerField(source='blogger.id', read_only=True)
    blogger_email = serializers.EmailField(source='blogger.email', read_only=True)
    blogger_name = serializers.CharField(source='blogger.blogger_profile.full_name', read_only=True)
    blogger_city = serializers.CharField(source='blogger.blogger_profile.city', read_only=True)
    blogger_gender = serializers.CharField(source='blogger.blogger_profile.gender', read_only=True)

    video_categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = UGCRequest
        fields = [
            'id',
            'product', 'product_id',
            'message','video_categories', 'status', 'created_at',
            'blogger_id', 'blogger_email', 'blogger_name',
            'blogger_city', 'blogger_gender',
        ]
        read_only_fields = ['created_at']


class FavoriteSerializer(serializers.ModelSerializer):
    product = PublicProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Favorite._meta.get_field('product').related_model.objects.all(),
        write_only=True,
        source='product'
    )

    class Meta:
        model = Favorite
        fields = ['id', 'product', 'product_id', 'added_at']
