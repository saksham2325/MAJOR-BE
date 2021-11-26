from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts import constants as ac
from accounts.manager import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(
        max_length=ac.FIRST_NAME_LAST_NAME_MAX_LENGTH)
    last_name = models.CharField(
        max_length=ac.FIRST_NAME_LAST_NAME_MAX_LENGTH, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email


class Group(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=ac.GROUP_TITLE_MAX_LENGTH, unique=True)
    description = models.CharField(
        max_length=ac.GROUP_DESCRIPTION_MAX_LENGTH, blank=True)

    def __str__(self):
        return self.title


class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class GroupInvitation(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class UserJiraToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jira_token = models.CharField(
        max_length=ac.JIRA_TOKEN_MAX_LENGTH, unique=True)
    expiry = models.DateTimeField(null=True)
