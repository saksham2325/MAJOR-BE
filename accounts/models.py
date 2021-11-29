from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.manager import UserManager
from accounts import constants as cc


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(
        max_length=cc.FIRST_NAME_LAST_NAME_MAX_LENGTH)
    last_name = models.CharField(
        max_length=cc.FIRST_NAME_LAST_NAME_MAX_LENGTH, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email


class Group(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=cc.GROUP_TITLE_MAX_LENGTH, unique=True)
    users = models.ManyToManyField(User, related_name="group_members")
    description = models.CharField(
        max_length=cc.GROUP_DESCRIPTION_MAX_LENGTH, blank=True)

    def __str__(self):
        return self.title


class GroupInvitation(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class UserJiraToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jira_token = models.CharField(
        max_length=cc.JIRA_TOKEN_MAX_LENGTH, unique=True)
    expiry = models.DateTimeField(null=True)
