from datetime import timedelta
from django.db import models
from django.utils import timezone

from accounts import constants as accounts_constants
from commons import constants as common_constants
from poker_backend import settings


class Timestamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class EmailVerification(Timestamp):
    email = models.EmailField(blank=True)
    name = models.CharField(
        max_length=accounts_constants.FIRST_NAME_LAST_NAME_MAX_LENGTH, blank=True)
    token_key = models.CharField(max_length=common_constants.TOKEN_MAX_LENGTH, unique=True)
    is_used = models.BooleanField(default=False)
    expiry = models.DateTimeField(default=timezone.now()+timedelta(minutes=common_constants.EXPIRY_TIME))
    purpose = models.PositiveSmallIntegerField(choices=common_constants.PURPOSE, default=common_constants.SIGNUP)


class Invitation(Timestamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=common_constants.INVITATION_STATUS, default=common_constants.PENDING)
    verification = models.ForeignKey(EmailVerification, on_delete=models.CASCADE)

    class Meta:
        abstract = True
