from django.db import models
from django.conf import settings
from brands.models import Product

User = settings.AUTH_USER_MODEL

class Collaboration(models.Model):
    STATUS_CHOICES = [
        ('address_provided', 'Адрес введён'),
        ('shipped', 'Отправлено брендом'),
        ('received', 'Получено блогером'),
        ('video_uploaded', 'Видео загружено'),
        ('verified', 'Видео подтверждено'),
        ('completed', 'Завершено'),
    ]

    blogger = models.ForeignKey(User, related_name='collaborations', on_delete=models.CASCADE)
    brand = models.ForeignKey(User, related_name='brand_collaborations', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    address = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    shipping_days = models.IntegerField(null=True, blank=True)

    video_link = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='address_provided')

    brand_rating = models.PositiveSmallIntegerField(null=True, blank=True)    # рейтинг от блогера
    blogger_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # рейтинг от бренда

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blogger} x {self.brand} ({self.product})"


class ChatMessage(models.Model):
    collaboration = models.ForeignKey(Collaboration, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} in {self.collaboration}"


class Review(models.Model):
    collaboration = models.ForeignKey(Collaboration, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    target = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_reviews")

    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('collaboration', 'author')

    def __str__(self):
        return f"Review from {self.author} to {self.target} (Collab {self.collaboration.id})"
