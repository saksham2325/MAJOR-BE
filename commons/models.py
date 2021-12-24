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

    PURPOSE = [
        (common_constants.SIGNUP, 'Signup'),
        (common_constants.GROUP, 'Group'),
        (common_constants.POKERBOARD, 'Pokerboard')
    ]

    email = models.EmailField(blank=True)
    name = models.CharField(
        max_length=accounts_constants.FIRST_NAME_LAST_NAME_MAX_LENGTH, blank=True)
    token_key = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    expiry = models.DateTimeField(default=timezone.now()+timedelta(minutes=30))
    purpose = models.PositiveSmallIntegerField(choices=PURPOSE, default=common_constants.SIGNUP)


class Invitation(Timestamp):

    INVITATION_STATUS = [
        (common_constants.PENDING, 'Pending'), 
        (common_constants.ACCEPTED, 'Accepted'), 
        (common_constants.DECLINED, 'Declined'), 
        (common_constants.CANCELLED, 'Cancelled')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=INVITATION_STATUS, default=common_constants.PENDING)
    verification = models.ForeignKey(EmailVerification, on_delete=models.CASCADE)

    class Meta:
        abstract = True
