from django.contrib import admin
from .models import CustomUser, ManagerProfile, BrandProfile, BloggerProfile

admin.site.register(CustomUser)

admin.site.register(ManagerProfile)
admin.site.register(BrandProfile)
admin.site.register(BloggerProfile)