from django.db import models
from django.contrib.auth.models import AbstractUser

from accounts.manager import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email


# class Group(models.Model):
#     admin = models.ForeignKey(User,on_delete=models.CASCADE)
#     title = models.CharField(max_length=50,unique=True)
#     description = models.CharField(max_length=1000,blank=True)

#     def __str__(self):
#         return self.title


# class UserGroup(models.Model):
#     user = models.ForeignKey(User,on_delete=models.CASCADE)
#     group = models.ForeignKey(Group,on_delete=models.CASCADE)


# class GroupInvitation(models.Model):
#     group = models.ForeignKey(Group,on_delete=models.CASCADE)