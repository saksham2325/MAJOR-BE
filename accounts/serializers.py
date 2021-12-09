from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework import serializers
from smtplib import SMTPException

from accounts import (constants as accounts_constants,
                      models as accounts_models)
from poker_backend import settings


class EmailVerifySerializer(serializers.Serializer):
    """This serializer is used to send email to verify users.It is not completed yet."""

    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data.get('email').lower()
        subject = 'Poker Planner account verification'
        message = f'Hi ${email} Welcome to Poker Planner. Please visit to the below link to verify your account. ThankYou'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        try:
            send_mail(subject, message, email_from, recipient_list)

        except SMTPException as e:
            """It will catch other errors related to SMTP."""

            return {"message": f'There was an error sending an email.${e}'}

        except Exception as e:
            """It will catch All other possible errors."""

            return {"message": f'Mail Sending Failed! ${e}'}

        return {"message": "Verification token send at email"}


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
