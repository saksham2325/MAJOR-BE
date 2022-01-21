import os

import django

from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter

import pokerboards.routing as routing
from pokerboards.token_auth import TokenAuthMiddleware, TokenAuthMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poker_backend.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": AsgiHandler(),
    "websocket": TokenAuthMiddleware(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
