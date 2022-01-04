from django.db import transaction
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from accounts import (constants as accounts_constants, models as accounts_models,
                      permissions as accounts_custom_permissions, serializers as accounts_serializers)


class SendToken(views.APIView):
    """Send token to user's email for account verification during signup."""

    authentication_classes = []
    permission_classes = []

    @transaction.atomic
    def post(self, request):
        serializer = accounts_serializers.EmailVerifySerializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())


class SendInvitation(views.APIView):
    permission_classes = [permissions.IsAuthenticated,
                          accounts_custom_permissions.ObjectAdmin]

    @transaction.atomic
    def post(self, request):
        serializer = accounts_serializers.SendInvitationSerializer(
            data=request.data,  context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())


class VerifyToken(generics.GenericAPIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = accounts_serializers.VerifyTokenSerializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())


class UserLoginView(ObtainAuthToken):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = accounts_serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = accounts_models.User.objects.get(email=request.data['email'])
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })


class UserLogoutView(views.APIView):

    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            data={'message': accounts_constants.USER_SUCCESSFULLY_LOGOUT}
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = accounts_models.User.objects.all()
    serializer_class = accounts_serializers.UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'list':
            permission_classes = [accounts_custom_permissions.ListPermission]
        else:
            permission_classes = [
                permissions.IsAuthenticated, accounts_custom_permissions.IsOwner]
        return [permission() for permission in permission_classes]


class GroupViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return accounts_serializers.GroupViewSerializer
        return accounts_serializers.GroupSerializer

    def get_queryset(self):
        return accounts_models.Group.objects.filter(admin=self.request.user)

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        if "users" in request.data:
            for user in request.data["users"]:
                group.users.remove(user)
            return Response(data={"message": accounts_constants.USER_REMOVED_FROM_GROUP})
        else:
            return super().destroy(request, *args, **kwargs)


class UserJiraTokenViewset(viewsets.ModelViewSet):
    queryset = accounts_models.UserJiraToken.objects.all()
    serializer_class = accounts_serializers.UserJiraTokenSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            permission_classes = [accounts_custom_permissions.ListPermission]
        else:
            permission_classes = [
                permissions.IsAuthenticated, accounts_custom_permissions.IsOwner]
        return [permission() for permission in permission_classes]


class UserGroups(generics.ListAPIView, generics.DestroyAPIView):

    serializer_class = accounts_serializers.UserGroupSerializer
    """This will return groups which are asscociated by authenticated user"""

    def get_queryset(self):
        return accounts_models.Group.objects.filter(users=self.request.user)

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        group.users.remove(request.user)
        return Response(data={'message': accounts_constants.SUCCESSFULLY_GROUP_LEFT})


class UpdatePassword(views.APIView):

    def get_object(self, queryset=None):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = accounts_serializers.ChangePasswordSerializer(
            data=request.data)

        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response({'message': accounts_constants.WRONG_PASSWORD}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({'status': status.HTTP_204_NO_CONTENT, 'message': accounts_constants.PASSWORD_UPDATED})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupInvitesViewSet(viewsets.ModelViewSet):
    serializer_class = accounts_serializers.GroupInvitesSerializer

    def get_queryset(self):
        return accounts_models.GroupInvitation.objects.filter(group__admin=self.request.user)


class UserGroupInvitesViewsets(viewsets.ModelViewSet):
    
    def get_queryset(self):
        email = self.request.query_params.get('email')
        if email:
            return accounts_models.GroupInvitation.objects.filter(verification__email=email)
        return accounts_models.GroupInvitation.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return accounts_serializers.UserGroupInvitesSerializer
        return accounts_serializers.UserGroupInvitesUpdateSerializer
