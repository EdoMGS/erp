# proizvodnja/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from .consumers import NotifikacijaConsumer

websocket_urlpatterns = [
    path('ws/notifikacije/', NotifikacijaConsumer.as_asgi()),
]
