from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

User = settings.AUTH_USER_MODEL


class Product(models.Model):
    brand = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)

    # Опциональная "обложка" (можно оставить пустой)
    image = models.ImageField(upload_to='product_images/cover/', blank=True, null=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=100)

    # Любые видео-категории, не фиксированные
    video_categories = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    file = models.ImageField(upload_to='product_images/%Y/%m/')
    alt = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)  # для сортировки
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image #{self.id} for {self.product_id}"


class ProductVideo(models.Model):
    product = models.ForeignKey(Product, related_name='videos', on_delete=models.CASCADE)
    file = models.FileField(upload_to='product_videos/%Y/%m/')  # mp4/mov/…
    title = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Video #{self.id} for {self.product_id}"


class Invitation(models.Model):
    brand = models.ForeignKey(User, related_name='invitations', on_delete=models.CASCADE)
    blogger = models.ForeignKey(User, related_name='invitations_received', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    message = models.TextField(blank=True)

    video_categories = ArrayField(
        base_field=models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Список типов видео, которые запрашивает бренд"
    )

    status = models.CharField(
        max_length=10,
        choices=[
            ('sent', 'Sent'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined'),
        ],
        default='sent'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invitation from {self.brand} to {self.blogger}"
