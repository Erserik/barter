# ugc_back/asgi.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ugc_back.settings')
django.setup()  # ✅ Должен быть до импортов collab.routing и моделей

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import collab.routing  # ✅ Только после django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            collab.routing.websocket_urlpatterns
        )
    ),
})
