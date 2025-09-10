from django.contrib import admin
from .models import Collaboration, ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_collab', 'sender_email', 'short_message', 'timestamp')
    list_filter = ('collaboration__product__name', 'sender')
    search_fields = ('message', 'sender__email', 'collaboration__blogger__email', 'collaboration__brand__email')
    ordering = ('-timestamp',)

    def short_message(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    short_message.short_description = 'Message'

    def sender_email(self, obj):
        return obj.sender.email
    sender_email.short_description = 'Sender'

    def short_collab(self, obj):
        return f"{obj.collaboration.blogger.email} ↔ {obj.collaboration.brand.email}"
    short_collab.short_description = 'Collaboration'

@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('id', 'blogger', 'brand', 'product', 'status', 'created_at')
    list_filter = ('status', 'product')
    search_fields = ('blogger__email', 'brand__email', 'product__name')
