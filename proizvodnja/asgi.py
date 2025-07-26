import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

from proizvodnja.consumers import NotifikacijaConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_system.settings")

# Standardni Django ASGI application
django_asgi_app = get_asgi_application()

# Channels routing
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/notifikacije/", NotifikacijaConsumer.as_asgi()),
                ]
            )
        ),
    }
)
