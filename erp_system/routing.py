from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from dashboard.routing import websocket_urlpatterns as dashboard_ws

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(URLRouter(dashboard_ws)),
    }
)
