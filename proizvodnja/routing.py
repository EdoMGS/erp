# proizvodnja/routing.py
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import NotifikacijaConsumer

websocket_urlpatterns = [
    path('ws/notifikacije/', NotifikacijaConsumer.as_asgi()),
]
