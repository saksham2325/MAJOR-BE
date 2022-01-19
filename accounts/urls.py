from django.db import router
from django.urls import include, path
from rest_framework import routers

from accounts import views as accounts_views


router = routers.DefaultRouter()
router.register(r'users', accounts_views.UserViewSet, basename="user")
router.register(r'groups', accounts_views.GroupViewSet, basename="group")
router.register(r'user-jiraToken',
                accounts_views.UserJiraTokenViewset, basename="userJiraToken")
router.register(r'group-invites', accounts_views.GroupInvitesViewSet, basename="group-invites'")
router.register(r'user-group-invites', accounts_views.UserGroupInvitesViewsets, basename='user-group-invites')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', accounts_views.UserLoginView.as_view()),
    path('logout/', accounts_views.UserLogoutView.as_view()),
    path('user-groups/', accounts_views.UserGroups.as_view(), name='user-groups'),
    path('user-groups/<int:pk>/', accounts_views.UserGroups.as_view()),
    path('list-groups/',accounts_views.ListGroups.as_view()),
    path('update-password/<int:pk>/', accounts_views.UpdatePassword.as_view()),
    path('verify-signup-token/', accounts_views.VerifySignupToken.as_view(), name='verify-signup-token'),
    path('verify-group-token/', accounts_views.VerifyGroupToken.as_view(), name='verify-group-token'),
    path('verify-poker-token/', accounts_views.VerifyPokerToken.as_view(), name='verify-poker-token'),
    path('send-token/', accounts_views.SendToken.as_view(), name='send-token'),
    path('send-invitation/', accounts_views.SendInvitation.as_view(), name='send-invitation'),
]
