from django.db import router
from django.urls import include, path
from rest_framework import routers

from accounts import views as accounts_views

router = routers.DefaultRouter()
router.register(r'users', accounts_views.UserViewSet, basename="user")
router.register(r'groups', accounts_views.GroupViewSet, basename="group")
router.register(r'userJiraToken',
                accounts_views.UserJiraTokenViewset, basename="userJiraToken")

urlpatterns = [
    path('', include(router.urls)),
    path('login/', accounts_views.UserLoginView.as_view()),
    path('logout/', accounts_views.UserLogoutView.as_view()),
    path('userGroups/<int:pk>/', accounts_views.UserGroupsView.as_view()),
]
