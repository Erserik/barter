# bloggers/views.py

from rest_framework import generics, permissions
from .models import UGCRequest, Favorite
from .serializers import UGCRequestSerializer, FavoriteSerializer, BloggerProfileSerializer
from accounts.models import BloggerProfile
from rest_framework.exceptions import NotFound


class IsBlogger(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'blogger')

class UGCRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = UGCRequestSerializer
    permission_classes = [IsBlogger]

    def get_queryset(self):
        return UGCRequest.objects.filter(blogger=self.request.user)

    def perform_create(self, serializer):
        serializer.save(blogger=self.request.user)

class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsBlogger]

    def get_queryset(self):
        return Favorite.objects.filter(blogger=self.request.user)

    def perform_create(self, serializer):
        serializer.save(blogger=self.request.user)

class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsBlogger]

    def get_object(self):
        favorite_id = self.kwargs.get("pk")
        try:
            return Favorite.objects.get(id=favorite_id, blogger=self.request.user)
        except Favorite.DoesNotExist:
            raise NotFound(detail="Favorite not found.")


class BloggerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BloggerProfileSerializer
    permission_classes = [IsBlogger]

    def get_object(self):
        return BloggerProfile.objects.get(user=self.request.user)

class PublicBloggerListView(generics.ListAPIView):
    serializer_class = BloggerProfileSerializer
    queryset = BloggerProfile.objects.all()
    permission_classes = []

class BloggerByCategoryView(generics.ListAPIView):
    serializer_class = BloggerProfileSerializer
    permission_classes = []

    def get_queryset(self):
        category = self.kwargs.get("category")
        return BloggerProfile.objects.filter(category__iexact=category)


class PublicBloggerDetailView(generics.RetrieveAPIView):
    serializer_class = BloggerProfileSerializer
    permission_classes = []

    def get_object(self):
        user_id = self.kwargs["id"]
        return BloggerProfile.objects.get(user__id=user_id)

from rest_framework import generics, permissions
from brands.models import Invitation
from .serializers import InvitationSerializer

class MyInvitationsView(generics.ListAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Invitation.objects.filter(blogger=self.request.user)

from brands.models import Invitation
from .serializers import InvitationSerializer

class InvitationUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Invitation.objects.filter(blogger=self.request.user)

class UGCRequestDeleteView(generics.DestroyAPIView):
    serializer_class = UGCRequestSerializer
    permission_classes = [IsBlogger]

    def get_object(self):
        ugc_id = self.kwargs.get("pk")
        try:
            return UGCRequest.objects.get(id=ugc_id, blogger=self.request.user)
        except UGCRequest.DoesNotExist:
            raise NotFound(detail="UGC request not found.")
