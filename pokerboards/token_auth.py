from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token

from accounts import models as accounts_models


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_key = headers[b'authorization'].decode(
                "utf-8").split(', ')[-1]
            user = Token.objects.get(key=token_key).user
            scope['user']=user
        return await self.app(scope, receive, send)


def TokenAuthMiddlewareStack(inner): return TokenAuthMiddleware(
    AuthMiddlewareStack(inner))
