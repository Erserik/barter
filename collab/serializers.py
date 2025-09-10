from rest_framework import serializers
from .models import Collaboration, ChatMessage
from brands.serializers import PublicProductSerializer
from accounts.models import BrandProfile, BloggerProfile

class CollaborationSerializer(serializers.ModelSerializer):
    product = PublicProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Collaboration._meta.get_field('product').related_model.objects.all(),
        source='product',
        write_only=True,
        required=False  # теперь не обязательно
    )

    class Meta:
        model = Collaboration
        fields = [
            'id',
            'blogger', 'brand',
            'product', 'product_id',
            'address', 'tracking_number', 'shipping_days',
            'video_link', 'status', 'created_at'
        ]
        read_only_fields = ['created_at']

    def create(self, validated_data):
        # Попробуем получить product из invitations или ugc_request
        invitations = self.initial_data.get("invitations")
        ugc_request = self.initial_data.get("ugc_request")

        if "product" not in validated_data:
            if invitations:
                from brands.models import Invitation  # или импорт выше
                inv = Invitation.objects.get(id=invitations)
                validated_data["product"] = inv.product
            elif ugc_request:
                from bloggers.models import UGCRequest  # или импорт выше
                req = UGCRequest.objects.get(id=ugc_request)
                validated_data["product"] = req.product
            else:
                raise serializers.ValidationError({"product_id": "Product must be provided via invitation or ugc_request."})

        return super().create(validated_data)

from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    target = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'collaboration', 'author', 'target', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'author', 'target', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        request = self.context['request']
        author = request.user
        collaboration = validated_data['collaboration']

        if author == collaboration.blogger:
            target = collaboration.brand
        elif author == collaboration.brand:
            target = collaboration.blogger
        else:
            raise serializers.ValidationError("You are not a participant of this collaboration.")

        validated_data['author'] = author
        validated_data['target'] = target

        if Review.objects.filter(collaboration=collaboration, author=author).exists():
            raise serializers.ValidationError("You have already left a review for this collaboration.")

        return super().create(validated_data)

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)


    class Meta:
        model = ChatMessage
        fields = ['id', 'collaboration', 'sender_id', 'sender_username','sender_name', 'message', 'timestamp']
