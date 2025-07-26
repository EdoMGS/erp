from django.urls import re_path

from . import consumers
from .consumers import BreakEvenConsumer

websocket_urlpatterns = [
    re_path(r"ws/dashboard/$", consumers.DashboardConsumer.as_asgi()),
    re_path(r"ws/break-even/$", BreakEvenConsumer.as_asgi()),
]
