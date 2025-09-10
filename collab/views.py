from django.db.models import Q
from rest_framework import viewsets, permissions, generics, status
from .models import Collaboration, Review, ChatMessage
from .serializers import CollaborationSerializer, ReviewSerializer, ChatMessageSerializer

from django.db.models import Avg, Count
from rest_framework.views import APIView
from rest_framework.response import Response

class CollaborationViewSet(viewsets.ModelViewSet):
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Collaboration.objects.filter(
            Q(blogger=user) | Q(brand=user)
        )

    def perform_create(self, serializer):
        serializer.save()


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Review.objects.filter(models.Q(author=user) | models.Q(target=user))

class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]  # или [] если публичный доступ

    def get_queryset(self):
        collab_id = self.kwargs.get('collab_id')
        return Review.objects.filter(collaboration__id=collab_id)

class ChatHistoryView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        collab_id = self.kwargs['collab_id']
        return ChatMessage.objects.filter(collaboration_id=collab_id).order_by('timestamp')

class UserRatingView(APIView):
    # 🔓 доступен всем без токена
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id: int):
        agg = Review.objects.filter(target_id=user_id).aggregate(
            avg=Avg('rating'),
            count=Count('id'),
        )
        avg = agg['avg'] or 0.0
        count = agg['count'] or 0

        # распределение по звёздам
        distribution = (
            Review.objects
            .filter(target_id=user_id)
            .values('rating')
            .annotate(n=Count('id'))
        )
        dist_map = {d['rating']: d['n'] for d in distribution}
        full_dist = {str(star): dist_map.get(star, 0) for star in range(5, 0, -1)}

        return Response({
            "user_id": user_id,
            "avg_rating": round(float(avg), 2),
            "max_rating": 5,
            "reviews_count": count,
            "distribution": full_dist,
        }, status=status.HTTP_200_OK)