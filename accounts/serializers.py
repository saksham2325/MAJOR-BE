from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers
from smtplib import SMTPException

from accounts import (constants as accounts_constants,
                      models as accounts_models, tasks as accounts_tasks)
from commons import (models as common_models, utils)


class EmailVerifySerializer(serializers.Serializer):
    """This serializer is used to send email to verify users for signup.It is not completed yet."""

    email = serializers.EmailField()
    name = serializers.CharField()
    purpose = serializers.IntegerField()

    def create(self, validated_data):
        email = validated_data.get('email').lower()
        name = validated_data.get('name')
        purpose = validated_data.get('purpose')
        token_key = utils.token_generator()

        with transaction.atomic():
            common_models.EmailVerification.objects.create(
                email=email, name=name, token_key=token_key, purpose=purpose)
            absurl = f"{accounts_constants.BASE_URL}/signup?token={token_key}&email={email}"
            subject = accounts_constants.EMAIL_VERIFICATION_SUBJECT
            message = f"Hi {name} Welcome to Poker Planner. Please visit to the below link to verify your account. \n{absurl}\n copy the link and paste in your browser in case link does not work"
            try:
                accounts_tasks.send_verification_mail.delay(
                    subject, email, message)

            except SMTPException as e:
                """It will catch other errors related to SMTP."""

                return {"message": f'There was an error sending an email.${e}'}

            except Exception as e:
                """It will catch All other possible errors."""

                return {"message": f'Mail Sending Failed! ${e}'}

            return {"message": accounts_constants.TOKEN_SENT}


class SendInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.IntegerField()
    id = serializers.IntegerField()

    def create(self, validated_data):
        email = validated_data.get('email').lower()
        purpose = validated_data.get('purpose')
        id = validated_data.get('id')
        token_key = utils.token_generator()

        with transaction.atomic():
            verification_obj = common_models.EmailVerification.objects.create(
                email=email, token_key=token_key, purpose=purpose)
            absurl = f"{accounts_constants.BASE_URL}/signup?token={token_key}&email={email}"
            
            if purpose == accounts_constants.GROUP_INVITATION_PURPOSE:
                subject = accounts_constants.GROUP_INVITATION_SUBJECT
                message = f"Hi Welcome to Poker Planner. Please visit to the below link to join the  group. \n{absurl}\n Copy the link and paste in your browser in case link does not work"
                accounts_models.GroupInvitation.objects.create(
                    group_id=id, verification_id=verification_obj.id)
            else:
                """for pokerboard Invitation."""
                pass
            try:
                accounts_tasks.send_verification_mail.delay(
                    subject, email, message)

            except SMTPException as e:
                """It will catch other errors related to SMTP."""

                return {"message": f'There was an error sending an email.${e}'}

            except Exception as e:
                """It will catch All other possible errors."""

                return {"message": f'Mail Sending Failed! ${e}'}

            return {"message": accounts_constants.INVITED}


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
        token = self.context['request'].data['token']
        if not common_models.EmailVerification.objects.filter(token_key=token).exists():
            return user
        
        email_verification_obj = common_models.EmailVerification.objects.get(token_key=token)
        if accounts_models.GroupInvitation.objects.filter(verification=email_verification_obj).exists():
            group_invitation_obj = accounts_models.GroupInvitation.objects.get(verification=email_verification_obj)
            group_obj = accounts_models.Group.objects.get(title=group_invitation_obj.group)
            group_obj.users.add(user)
            group_obj.save()
            group_invitation_obj.status=accounts_constants.INVITATION_STATUS_ACCEPTED
        email_verification_obj.is_used=True
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


class GroupSerializer(serializers.ModelSerializer):

    # users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = accounts_models.Group
        fields = ['id', 'admin', 'title', 'description', 'users']

    def validated_admin(self, admin):
        """applying validator so that admin cannot be updated"""

        if self.instance is not None and self.instance.admin != admin:
            raise serializers.ValidationError(
                accounts_constants.ADMIN_CANNOT_UPDATE)
        return admin

    def create(self, validated_data):
        """override create method to add admin in the group by default when the group created."""
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


class UserSearchSerializer(UserSerializer):

    class Meta:
        model = accounts_models.User
        fields = ['first_name', 'last_name', 'email']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
