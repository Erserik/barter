from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

User = settings.AUTH_USER_MODEL


class Product(models.Model):
    brand = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)

    image = models.ImageField(upload_to='product_images/cover/', blank=True, null=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)

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
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image #{self.id} for {self.product_id}"


class ProductVideo(models.Model):
    product = models.ForeignKey(Product, related_name='videos', on_delete=models.CASCADE)
    file = models.FileField(upload_to='product_videos/%Y/%m/')
    title = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Video #{self.id} for {self.product_id}"
