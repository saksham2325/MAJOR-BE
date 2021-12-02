from rest_framework import authentication,filters, generics, permissions, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts import (constants as ac, models as accounts_models,
                      permissions as custom_permissions, serializers as account_serializers)


class UserLoginView(ObtainAuthToken):

    def post(self, request):
        serializer = account_serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = accounts_models.User.objects.get(email=request.data['email'])
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key
        })


class UserLogoutView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        user = Token.objects.get(key=token).user
        user.auth_token.delete()
        return Response(
            data={'message': ac.USER_SUCCESSFULLY_LOGOUT}
        )


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    queryset = accounts_models.User.objects.all()
    serializer_class = account_serializers.UserSerializer

    """trying to fetch user by email but not working"""
    # @detail_route(methods=['get'], url_path='retrieve_by_username/(?P<username>\w+)')
    # def getByUsername(self, request, username):
    #     user = get_object_or_404(User, username=username)
    #     return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [
                permissions.IsAuthenticated, custom_permissions.IsOwner]
        return [permission() for permission in permission_classes]


class GroupViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = account_serializers.GroupSerializer

    def get_queryset(self):
        return accounts_models.Group.objects.filter(admin=self.request.user)

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        if "users" in request.data:
            for user in request.data["users"]:
                group.users.remove(user)
            return Response(data={"message": ac.USER_REMOVED_FROM_GROUP})
        else:
            return super().destroy(request, *args, **kwargs)


class UserJiraTokenViewset(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    queryset = accounts_models.UserJiraToken.objects.all()
    serializer_class = account_serializers.UserJiraTokenSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            permission_classes = [custom_permissions.ListPermission]
        else:
            permission_classes = [custom_permissions.IsOwner]
        return [permission() for permission in permission_classes]


class UserGroupsView(generics.ListAPIView, generics.DestroyAPIView):

    def destroy(self, request, *args, **kwargs):
        token = self.request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        user = Token.objects.get(key=token).user
        group = self.get_object()
        group.users.remove(user)
        return Response(data={"message": "Group left successfully!"})


"""trying to fetch user by email but not working"""
# class SearchUser(generics.ListAPIView):
    
#     serializer_class = account_serializers.SearchUserSerializer
#     queryset = accounts_models.User.objects.all()
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['email']
