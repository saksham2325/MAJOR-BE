from datetime import timedelta
from django.utils import timezone
import uuid

from accounts import constants as accounts_constants


def token_generator():
    token = uuid.uuid4()
    token_key = str(token)
    return token_key

def is_expired(creation_time):
    return timezone.now() > creation_time+timedelta(minutes=accounts_constants.EXPIRY_TIME)
