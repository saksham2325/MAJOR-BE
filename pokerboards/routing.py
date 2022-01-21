from django.urls import path, re_path

from pokerboards import consumer as poker_consumers


websocket_urlpatterns = [
     # re_path(r'ws/pokerboard/(?P<pokerboard_id>\w+)/$', poker_consumers.PokerConsumer.as_asgi()),
     path('ws/pokerboard/<int:pokerboard_id>/', poker_consumers.PokerConsumer.as_asgi(), name='ws-pokerboard'),
]