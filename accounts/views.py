from datetime import time
from django.utils import timezone
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import views

from accounts import (constants as accounts_constants, models as accounts_models,
                      permissions as custom_permissions, serializers as account_serializers)
from commons import models as common_models


class SendToken(views.APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        serializer = account_serializers.EmailVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())
    

class SendInvitation(views.APIView):
    permission_classes = [permissions.IsAuthenticated, custom_permissions.GroupAdmin]
    
    def post(self, request):
        serializer = account_serializers.SendInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())
    

class VerifyToken(generics.GenericAPIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        token = request.data['token']
        if not common_models.EmailVerification.objects.filter(token_key=token).exists():
            return Response({'message':accounts_constants.INVALID_TOKEN},status=status.HTTP_400_BAD_REQUEST)
        
        email_verification_obj = common_models.EmailVerification.objects.get(token_key=token)
        
        if email_verification_obj.is_used or timezone.now()>email_verification_obj.expiry:
            print('email_expiry', email_verification_obj.expiry)
            print('time_now',timezone.now())
            return Response({'message':accounts_constants.TOKEN_EXPIRED_OR_ALREADY_USED}, status=status.HTTP_400_BAD_REQUEST)
            
        if email_verification_obj.purpose == accounts_constants.SIGNUP_PURPOSE:
            """Check whether user already exist with the same account, it could be possible that user registered himself with another verification link and trying to register again with different link."""
            
            if accounts_models.User.objects.filter(email=email_verification_obj.email).exists():
                return Response({'message': accounts_constants.USER_ALREADY_EXIST}, status=status.HTTP_204_NO_CONTENT)
            return Response({'message':accounts_constants.SUCCESSFULLY_VERIFY_ACCOUNT}, status=status.HTTP_200_OK)
        
        elif email_verification_obj.purpose == accounts_constants.GROUP_INVITATION_PURPOSE:
            
            group_invitation_obj = accounts_models.GroupInvitation.objects.get(verification=email_verification_obj.id)
            if group_invitation_obj.status==accounts_constants.INVITATION_STATUS_CANCELLED:
                return Response({'message':accounts_constants.INVITATION_CANCELLED}, status=status.HTTP_204_NO_CONTENT)
            
            if accounts_models.User.objects.filter(email=email_verification_obj.email).exists():
                """If user already exist then add him to the group and mark invitation status in GroupInvitation table as "accepted" and mark "is_used" in EmailVerification table true. and display message in frontend (added to the group, pls login)."""
                
                user = accounts_models.User.objects.get(email=email_verification_obj.email)
                group_obj = accounts_models.Group.objects.get(title=group_invitation_obj.group)
                group_obj.users.add(user)
                group_obj.save()
                group_invitation_obj.status=accounts_constants.INVITATION_STATUS_ACCEPTED
                email_verification_obj.is_used=True
                email_verification_obj.save()
                return Response({'message': accounts_constants.USER_ADDED},status=status.HTTP_204_NO_CONTENT)
            else:
                """ redirect to signup page and allow user to register in the app without any further verification. and user will automatically added to the group after successful signup."""
                
                return Response({'message':accounts_constants.ADD_AFTER_SIGNUP},status=status.HTTP_200_OK)
        else:
            # if invitation purpose is 2(pokerboard invite)
            pass
    
    
class UserLoginView(ObtainAuthToken):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = account_serializers.LoginSerializer(data=request.data)
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
        self.request.user.auth_token.delete()
        return Response(
            data={'message': accounts_constants.USER_SUCCESSFULLY_LOGOUT}
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = accounts_models.User.objects.all()
    serializer_class = account_serializers.UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'list' :
            permission_classes = [custom_permissions.ListPermission]
        else:
            permission_classes = [
                permissions.IsAuthenticated, custom_permissions.IsOwner]
        return [permission() for permission in permission_classes]


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = account_serializers.GroupSerializer

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
    serializer_class = account_serializers.UserJiraTokenSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            permission_classes = [custom_permissions.ListPermission]
        else:
            permission_classes = [permissions.IsAuthenticated, custom_permissions.IsOwner]
        return [permission() for permission in permission_classes]


class UserGroupsView(generics.ListAPIView, generics.DestroyAPIView):

    serializer_class = account_serializers.UserGroupSerializer
    """This will return groups which are asscociated by authenticated user"""

    def get_queryset(self):
        token = self.request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        user = Token.objects.get(key=token).user
        return accounts_models.Group.objects.filter(users=user)

    def destroy(self, request, *args, **kwargs):
        token = self.request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        user = Token.objects.get(key=token).user
        group = self.get_object()
        group.users.remove(user)
        return Response(data={'message': accounts_constants.SUCCESSFULLY_GROUP_LEFT})


class UserFetchBy(generics.ListAPIView):
    """This is used to get users by email"""
    
    authentication_classes = []
    permission_classes = []
    serializer_class = account_serializers.UserSearchSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['email']

    def get_queryset(self):
        return accounts_models.User.objects.all()


class UpdatePassword(views.APIView):

    def get_object(self, queryset=None):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = account_serializers.ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response({'status':status.HTTP_400_BAD_REQUEST, 'message':accounts_constants.WRONG_PASSWORD})
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({'status':status.HTTP_204_NO_CONTENT, 'message':accounts_constants.PASSWORD_UPDATED})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
