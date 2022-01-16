from django.db import router
from django.urls import include, path
from rest_framework import routers

from pokerboards import views as pokerboard_views


router = routers.DefaultRouter()
router.register(r'pokerboard', pokerboard_views.PokerboardViewsets, basename="pokerboard")

urlpatterns = [
    path('', include(router.urls)),
    path('user-pokerboard/', pokerboard_views.UserPokerboardView.as_view(), name='user-pokerboard'),
    path('user-pokerboard/<int:pk>/', pokerboard_views.UserPokerboardView.as_view()),
]
