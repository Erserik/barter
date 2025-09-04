# bloggers/models.py

from django.db import models
from django.conf import settings
from brands.models import Product
from accounts.models import BloggerProfile  # Используем существующую модель

from django.contrib.postgres.fields import ArrayField

User = settings.AUTH_USER_MODEL

class UGCRequest(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Отправлено'),
        ('accepted', 'Принято'),
        ('shipped', 'Доставлено'),
        ('received', 'Получено'),
        ('recorded', 'Снято видео'),
        ('completed', 'Завершено'),
        ('rejected', 'Отклонено'),
    ]

    blogger = models.ForeignKey(User, related_name='ugc_requests', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='ugc_requests', on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    video_categories = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Типы видео, которые блогер планирует создать"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blogger.email} → {self.product.name}"

class Favorite(models.Model):
    blogger = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='favorited_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blogger', 'product')

    def __str__(self):
        return f"{self.blogger.email} ❤️ {self.product.name}"