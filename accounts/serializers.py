from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers, status
from smtplib import SMTPException

from accounts import (constants as accounts_constants,
                      models as accounts_models, tasks as accounts_tasks)
from commons import (models as common_models, utils)
from pokerboards import (models as pokerboard_models)


class EmailVerifySerializer(serializers.Serializer):
    """
    This serializer is used to send email to verify users for signup.
    """
    email = serializers.EmailField()
    name = serializers.CharField()
    purpose = serializers.IntegerField()

    def validate_email(self, email):
        email = email.lower()
        if accounts_models.User.objects.filter(email__exact=email).exists():
            raise serializers.ValidationError(
                accounts_constants.USER_ALREADY_EXIST)
        return email

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.get('email').lower()
        name = validated_data.get('name')
        purpose = validated_data.get('purpose')
        token_key = utils.token_generator()
        common_models.EmailVerification.objects.create(
            email=email, name=name, token_key=token_key, purpose=purpose)
        absurl = f"{accounts_constants.BASE_URL}/verify-signup-token?token={token_key}"
        subject = accounts_constants.EMAIL_VERIFICATION_SUBJECT
        message = accounts_constants.SIGNUP_MESSAGE.format(name, absurl)
        try:
            accounts_tasks.send_verification_mail.delay(
                subject, email, message)

        except SMTPException as e:
            """
            It will catch other errors related to SMTP.
            """
            raise serializers.ValidationError(
                accounts_constants.EMAIL_SEND_ERROR)

        except Exception as e:
            """
            It will catch All other possible errors.
            """
            raise serializers.ValidationError(
                accounts_constants.EMAIL_SEND_FAILED)

        return validated_data


class SendInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.IntegerField()
    id = serializers.IntegerField()

    def validate(self, data):
        email = data.get('email').lower()
        purpose = data.get('purpose')
        id = data.get('id')
        if purpose == accounts_constants.GROUP_INVITATION_PURPOSE and accounts_models.User.objects.filter(email=email).exists():
            user = accounts_models.User.objects.get(email=email)
            """
            Check if user is already present in the group if so then raise error.
            """
            if accounts_models.Group.objects.filter(id=id, users=user).exists():
                raise serializers.ValidationError(
                    accounts_constants.ALREADY_IN_GROUP)

            """
            Check if user is already invited and invitation status is pending then cannot reinvite.
            """
            if accounts_models.GroupInvitation.objects.filter(group_id=id, status=accounts_constants.INVITATION_STATUS_PENDING, user=user).exists():
                raise serializers.ValidationError(
                    accounts_constants.ALREADY_INVITED)
            return data
        elif purpose == accounts_constants.POKERBOARD_INVITATION_PURPOSE and accounts_models.User.objects.filter(email=email).exists():
            role = self.context['request'].query_params.get('role')
            user = accounts_models.User.objects.get(email=email)
            """
            if user exist in the app and he is already invited in the same Pokerboard for the same role and invitation is still pending, then user cannot be reinvite
            """
            if pokerboard_models.PokerboardInvitation.objects.filter(
                    user=user, pokerboard_id=id, status=accounts_constants.INVITATION_STATUS_PENDING, role=[role]).exists():
                raise serializers.ValidationError(
                    accounts_constants.ALREADY_INVITED)
            return data
        return data

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.get('email').lower()
        purpose = validated_data.get('purpose')
        id = validated_data.get('id')
        token_key = utils.token_generator()

        verification_obj = common_models.EmailVerification.objects.create(
            email=email, token_key=token_key, purpose=purpose)

        if purpose == accounts_constants.GROUP_INVITATION_PURPOSE:
            subject = accounts_constants.GROUP_INVITATION_SUBJECT
            absurl = f"{accounts_constants.BASE_URL}/verify-group-token?token={token_key}"
            message = accounts_constants.GROUP_INVITATION_MESSAGE.format(
                absurl)
            if accounts_models.User.objects.filter(email=email).exists():
                """if user exist in the app and he is already invited in the same group and invitation is still pending, then user cannot be reinvite"""

                user = accounts_models.User.objects.get(email=email)
                accounts_models.GroupInvitation.objects.create(
                    group_id=id, user_id=user.id, verification_id=verification_obj.id)
            else:
                accounts_models.GroupInvitation.objects.create(
                    group_id=id, verification_id=verification_obj.id)
        else:
            """
            for pokerboard Invitation.
            """
            role = self.context['request'].query_params.get('role')
            subject = accounts_constants.POKERBOARD_INVITATION_SUBJECT
            absurl = f"{accounts_constants.BASE_URL}/verify-poker-token?token={token_key}"
            message = accounts_constants.POKERBOARD_INVITATION_MESSAGE.format(
                accounts_constants.USER_ROLE[role], absurl)
            if accounts_models.User.objects.filter(email=email).exists():
                user = accounts_models.User.objects.get(email=email)
                pokerboard_models.PokerboardInvitation.objects.create(
                    pokerboard_id=id, user_id=user.id, verification_id=verification_obj.id, role=[role])
            else:
                pokerboard_models.PokerboardInvitation.objects.create(
                    pokerboard_id=id, verification_id=verification_obj.id, role=[role])
        try:
            accounts_tasks.send_verification_mail.delay(
                subject, email, message)

        except SMTPException as e:
            """
            It will catch other errors related to SMTP.
            """
            raise serializers.ValidationError(
                accounts_constants.EMAIL_SEND_FAILED)

        except Exception as e:
            """
            It will catch All other possible errors.
            """
            raise serializers.ValidationError(
                accounts_constants.INVITATION_FAILED)

        return validated_data


class SendInvitationToGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate(self, data):
        game_id = data.get('id')
        group_title = self.context['request'].query_params.get('group_title')
        role = self.context['request'].query_params.get('role')
        group = accounts_models.Group.objects.get(title=group_title)
        group_users = []
        users = group.users.all()
        for user in users:
            if not pokerboard_models.UserPokerboard.objects.filter(user=user, pokerboard_id=game_id).exists() and not pokerboard_models.PokerboardInvitation.objects.filter(user=user, pokerboard_id=game_id, status=accounts_constants.INVITATION_STATUS_PENDING, role=[role]).exists():
                group_users.append(user)
        """
        If all the group users are already invited or they already exist in the pokerboard.Then nothing to invite.
        """
        if len(group_users) == 0:
            raise serializers.ValidationError(
                accounts_constants.ALREADY_EXIST_OR_INVITED)
        data['group_users'] = group_users
        return data

    @transaction.atomic
    def create(self, validated_data):
        game_id = validated_data.get('id')
        role = self.context['request'].query_params.get('role')
        subject = accounts_constants.POKERBOARD_INVITATION_SUBJECT
        try:
            for user in validated_data['group_users']:
                token_key = utils.token_generator()
                verification_obj = common_models.EmailVerification.objects.create(
                    email=user.email, token_key=token_key, purpose=accounts_constants.POKERBOARD_INVITATION_PURPOSE)
                pokerboard_models.PokerboardInvitation.objects.create(
                    pokerboard_id=game_id, user_id=user.id, verification_id=verification_obj.id, role=[role])
                absurl = f"{accounts_constants.BASE_URL}/verify-poker-token?token={token_key}"
                message = accounts_constants.POKERBOARD_INVITATION_MESSAGE.format(
                    accounts_constants.USER_ROLE[role], absurl)
                accounts_tasks.send_verification_mail.delay(
                subject, user.email, message)
        except SMTPException as e:
            """
            It will catch other errors related to SMTP.
            """
            raise serializers.ValidationError(
                accounts_constants.EMAIL_SEND_FAILED)
        return validated_data


class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    def get_verification_object(self, token):
        return common_models.EmailVerification.objects.get(token_key=token)

    def validate(self, data):
        token = data['token']
        if not common_models.EmailVerification.objects.filter(token_key=token).exists():
            raise serializers.ValidationError(accounts_constants.INVALID_TOKEN)

        email_verification_obj = self.get_verification_object(token)

        if email_verification_obj.is_used or utils.is_expired(email_verification_obj.created_at):
            raise serializers.ValidationError(
                accounts_constants.TOKEN_EXPIRED_OR_ALREADY_USED)

        return data

    def get_user(self, email):
        if accounts_models.User.objects.filter(email=email).exists():
            return accounts_models.User.objects.get(email=email)
        return None

    @property
    def data(self):
        return self.instance


class VerifySignupTokenSerializer(VerifyTokenSerializer):

    def validate(self, data):
        super().validate(data)
        token = data.get('token')
        email_verification_obj = self.get_verification_object(token)
        """
        Check whether user already exist with the same email, it could be possible that user registered himself with another verification link and trying to register again with different link.
        """
        user = self.get_user(email_verification_obj.email)
        if user is not None:
            raise serializers.ValidationError(
                accounts_constants.USER_ALREADY_EXIST)

        return data

    def create(self, validated_data):
        token = validated_data.get('token')
        email_verification_obj = self.get_verification_object(token)
        return {'message': accounts_constants.SUCCESSFULLY_VERIFY_ACCOUNT, 'email': {email_verification_obj.email}, 'name': {email_verification_obj.name}, 'status': status.HTTP_200_OK}


class VerifyGroupTokenSerializer(VerifyTokenSerializer):

    def validate(self, data):
        super().validate(data)
        email_verification_obj = self.get_verification_object(data['token'])
        if not accounts_models.GroupInvitation.objects.filter(verification=email_verification_obj.id).exists():
            raise serializers.ValidationError(
                accounts_constants.SOMETHING_WENT_WRONG)
        group_invitation_obj = accounts_models.GroupInvitation.objects.get(
            verification=email_verification_obj.id)
        """
        Check if Group Manager/admin cancelled the status, if yes then simply return.
        """
        if group_invitation_obj.status == accounts_constants.INVITATION_STATUS_CANCELLED:
            raise serializers.ValidationError(
                accounts_constants.INVITATION_CANCELLED)
        """
        Check If user already declined the invitation from app and try to accept invitation from email.
        """
        if group_invitation_obj.status == accounts_constants.INVITATION_STATUS_DECLINED:
            raise serializers.ValidationError(
                accounts_constants.INVITATION_DECLINED)

        return data

    def create(self, validated_data):
        email_verification_obj = self.get_verification_object(
            validated_data['token'])
        group_invitation_obj = accounts_models.GroupInvitation.objects.get(
            verification=email_verification_obj.id)
        user = self.get_user(email_verification_obj.email)

        if user is not None:
            """
            If user already exist then add him to the group and mark invitation status in GroupInvitation table as "accepted" and mark "is_used" in EmailVerification table true. and display message in frontend (added to the group, pls login).
            """
            group_obj = accounts_models.Group.objects.get(
                title=group_invitation_obj.group)
            group_obj.users.add(user)
            group_obj.save()
            group_invitation_obj.status = accounts_constants.INVITATION_STATUS_ACCEPTED
            group_invitation_obj.save()
            email_verification_obj.is_used = True
            email_verification_obj.save()
            return {'message': accounts_constants.USER_ADDED, 'status': status.HTTP_201_CREATED}
        else:
            """
            Redirect to signup page and allow user to register in the app without any further verification. and user will automatically added to the group after successful signup.
            """
            return {'message': accounts_constants.ADD_AFTER_SIGNUP, 'email': {email_verification_obj.email}, 'name': {email_verification_obj.name}, 'status': status.HTTP_200_OK}


class VerifyPokerTokenSerializer(VerifyTokenSerializer):

    def validate(self, data):
        super().validate(data)
        email_verification_obj = self.get_verification_object(data['token'])
        if not pokerboard_models.PokerboardInvitation.objects.filter(verification=email_verification_obj.id).exists():
            raise serializers.ValidationError(
                accounts_constants.SOMETHING_WENT_WRONG)
        poker_invitation_obj = pokerboard_models.PokerboardInvitation.objects.get(
            verification=email_verification_obj.id)
        """
        Check if Group Manager/admin cancelled the status, if yes then simply return.
        """
        if poker_invitation_obj.status == accounts_constants.INVITATION_STATUS_CANCELLED:
            raise serializers.ValidationError(
                accounts_constants.INVITATION_CANCELLED)
        """
        Check If user already declined the invitation from app and try to accept invitation from email.
        """
        if poker_invitation_obj.status == accounts_constants.INVITATION_STATUS_DECLINED:
            raise serializers.ValidationError(
                accounts_constants.INVITATION_DECLINED)

        return data

    def create(self, validated_data):
        email_verification_obj = self.get_verification_object(
            validated_data['token'])
        poker_invitation_obj = pokerboard_models.PokerboardInvitation.objects.get(
            verification=email_verification_obj.id)
        user = self.get_user(email_verification_obj.email)

        if user is not None:
            """
            If user already exist then add him to the poker and mark invitation status in GroupInvitation table as "accepted" and mark "is_used" in EmailVerification table true. and display message in frontend (added to the group, pls login).
            """
            pokerboard_models.UserPokerboard.objects.create(
                user_id=user.id, pokerboard_id=poker_invitation_obj.pokerboard.id, role=poker_invitation_obj.role)
            poker_invitation_obj.status = accounts_constants.INVITATION_STATUS_ACCEPTED
            poker_invitation_obj.save()
            email_verification_obj.is_used = True
            email_verification_obj.save()
            return {'message': accounts_constants.USER_ADDED, 'status': status.HTTP_201_CREATED}
        else:
            """
            Redirect to signup page and allow user to register in the app without any further verification. and user will automatically added to the group after successful signup.
            """
            return {'message': accounts_constants.ADD_AFTER_SIGNUP, 'email': {email_verification_obj.email}, 'name': {email_verification_obj.name}, 'status': status.HTTP_200_OK}


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)

    def validate(self, data):
        data['email'] = data['email'].lower()
        username = data.get('email')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(
                accounts_constants.INVALID_CREDENTIALS, code='authorization')
        else:
            return data


class UserReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = accounts_models.User
        fields = ['id', 'email', 'first_name', 'last_name']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = accounts_models.User
        fields = ['id', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validated_email(self, email):
        email = email.lower()
        if self.instance is not None and self.instance.email != email:
            raise serializers.ValidationError(
                accounts_constants.EMAIL_CANNOT_UPDATE)
        return email

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        """
        once user created successfully,access invitation token from requested data and check if the user is registering through group/pokerboard invitation, if yes then update the group invitation status and directly adding user in the group.
        """
        token = self.context['request'].data['token']
        if not common_models.EmailVerification.objects.filter(token_key=token).exists():
            return user

        email_verification_obj = common_models.EmailVerification.objects.get(
            token_key=token)

        if accounts_models.GroupInvitation.objects.filter(verification=email_verification_obj).exists():
            """
            If user is coming through Group Invitation.
            """
            group_invitation_obj = accounts_models.GroupInvitation.objects.get(
                verification=email_verification_obj)
            group_obj = accounts_models.Group.objects.get(
                title=group_invitation_obj.group)
            group_obj.users.add(user)
            group_obj.save()
            group_invitation_obj.status = accounts_constants.INVITATION_STATUS_ACCEPTED
            group_invitation_obj.save()

        elif pokerboard_models.PokerboardInvitation.objects.filter(verification=email_verification_obj).exists():
            """
            If user is coming through Pokerboard Invitation
            """
            pokerboard_invitation_obj = pokerboard_models.PokerboardInvitation.objects.get(
                verification=email_verification_obj)
            pokerboard_models.UserPokerboard.objects.create(
                user_id=user.id, pokerboard_id=pokerboard_invitation_obj.pokerboard.id, role=pokerboard_invitation_obj.role)
            pokerboard_invitation_obj.status = accounts_constants.INVITATION_STATUS_ACCEPTED
            pokerboard_invitation_obj.save()
        email_verification_obj.is_used = True
        email_verification_obj.save()
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class GroupViewSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    admin = UserReadSerializer(read_only=True)

    class Meta:
        model = accounts_models.Group
        fields = ['id', 'admin', 'title', 'description', 'users']


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = accounts_models.Group
        fields = ['id', 'admin', 'title', 'description', 'users']

    def validated_admin(self, admin):
        """
        applying validator so that admin cannot be updated
        """
        if self.instance is not None and self.instance.admin != admin:
            raise serializers.ValidationError(
                accounts_constants.ADMIN_CANNOT_UPDATE)
        return admin

    def create(self, validated_data):
        """
        override create method to add admin in the group by default when the group created.
        """
        admin = self.context["request"].user
        validated_data["admin"] = admin
        if admin not in validated_data["users"]:
            validated_data["users"].append(admin)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "users" in validated_data:
            instance.users.add(*validated_data["users"])
        if "title" in validated_data:
            instance.title = validated_data["title"]
        if "description" in validated_data:
            instance.description = validated_data["description"]
        instance.save()
        return instance


class UserJiraTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = accounts_models.UserJiraToken
        fields = ['user', 'jira_token', 'expiry']


class UserGroupSerializer(GroupSerializer):
    users = UserSerializer(many=True, read_only=True)
    admin = UserSerializer(read_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class VerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = common_models.EmailVerification
        fields = ['id', 'email']


class GroupInvitesSerializer(serializers.ModelSerializer):
    """
    This serializer is to get the list of all group invitations group admin send.
    """

    group = GroupViewSerializer()
    verification = VerificationSerializer()

    class Meta:
        model = accounts_models.GroupInvitation
        fields = ['id', 'group', 'status', 'verification']


class UserGroupInvitesSerializer(serializers.ModelSerializer):
    """
    This serializer is to get the list of all group invitations user received.
    """

    group = GroupViewSerializer()

    class Meta:
        model = accounts_models.GroupInvitation
        fields = ['id', 'group', 'status']


class UserGroupInvitesUpdateSerializer(serializers.Serializer):
    """
    Thi serializer is to update invitation(accept/decline group invitation).If user will accept the invitation he will be added to the group.
    """
    status = serializers.IntegerField()

    def update(self, instance, validated_data):
        if validated_data['status'] == accounts_constants.INVITATION_STATUS_DECLINED:
            instance.status = accounts_constants.INVITATION_STATUS_DECLINED
            instance.save()
            return instance
        group_obj = accounts_models.Group.objects.get(title=instance.group)
        if instance.user is not None:
            group_obj.users.add(instance.user)
            group_obj.save()
            instance.status = accounts_constants.INVITATION_STATUS_ACCEPTED
            instance.save()
        return instance


class ListGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = accounts_models.Group
        fields = ['title']
