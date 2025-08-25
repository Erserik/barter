from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)  # для совместимости с AbstractUser
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('username', email)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('brand', 'Бренд'),
        ('blogger', 'Блогер'),
        ('manager', 'Менеджер'),
    )

    username = models.CharField(max_length=150, blank=True)  # Унаследовано, но нужно
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_confirmed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    def get_profile(self):
        if self.role == 'blogger':
            return getattr(self, 'blogger_profile', None)
        elif self.role == 'brand':
            return getattr(self, 'brand_profile', None)
        elif self.role == 'manager':
            return getattr(self, 'manager_profile', None)
        return None

class ManagerProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='manager_profile'
    )
    full_name = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name


class BrandProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='brand_profile'
    )
    full_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    city = models.CharField(max_length=100)
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.company_name


class BloggerProfile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Мужской'),
        ('female', 'Женский'),
    )

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='blogger_profile'
    )
    full_name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='blogger_avatar/', blank=True, null=True)
    city = models.CharField(max_length=100)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)  # ✅
    instagram = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    description = models.TextField(blank=True)



    def __str__(self):
        return self.full_name
