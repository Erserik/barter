from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CollaborationViewSet, ReviewViewSet, ChatHistoryView, ReviewListView, UserRatingView  # 👈 добавили ReviewViewSet

router = DefaultRouter()
router.register(r'collaborations', CollaborationViewSet, basename='collaboration')
router.register(r'reviews', ReviewViewSet)  # 👈 добавили эндпоинт отзывов

urlpatterns = [
    path('', include(router.urls)),
    path('chat/<int:collab_id>/', ChatHistoryView.as_view(), name='chat-history'),
    path('collaborations/<int:collab_id>/reviews/', ReviewListView.as_view(), name='collaboration-reviews'),
    path('users/<int:user_id>/rating/', UserRatingView.as_view(), name='user-rating'),

]
