# proizvodnja/routing.py
from django.urls import path

from .consumers import NotifikacijaConsumer

websocket_urlpatterns = [
    path("ws/notifikacije/", NotifikacijaConsumer.as_asgi()),
]
