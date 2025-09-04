# bloggers/urls.py

from django.urls import path
from .views import (
    UGCRequestListCreateView,
    FavoriteListCreateView,
    FavoriteDeleteView,
    BloggerProfileView,
    PublicBloggerListView,
    BloggerByCategoryView,
    PublicBloggerDetailView,
    MyInvitationsView,
    InvitationUpdateView,
    UGCRequestDeleteView
)

urlpatterns = [
    path('ugc-requests/', UGCRequestListCreateView.as_view(), name='ugc-request-list-create'),  # GET, POST
    path('ugc-requests/<int:pk>/', UGCRequestDeleteView.as_view(), name='ugc-request-delete'),  # DELETE ✅

    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list-create'),  # GET, POST
    path('favorites/<int:pk>/', FavoriteDeleteView.as_view(), name='favorite-delete'),

    path('me/profile/', BloggerProfileView.as_view(), name='blogger-profile'),  # GET, PATCH
    path('public/bloggers/', PublicBloggerListView.as_view(), name='blogger-list'),  # GET
    path('public/bloggers/category/<str:category>/', BloggerByCategoryView.as_view(), name='blogger-by-category'),
    # GET
    path('public/bloggers/<int:id>/', PublicBloggerDetailView.as_view(), name='public-blogger-detail'),

    path('my-invitations/', MyInvitationsView.as_view(), name='my-invitations'),
    path('my-invitations/<int:pk>/', InvitationUpdateView.as_view(), name='invitation-update'),
]

