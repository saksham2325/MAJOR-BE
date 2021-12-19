from celery import shared_task
from django.core.mail import send_mail
from django.urls import reverse

from accounts import constants as accounts_constants
from poker_backend import settings


@shared_task
def send_verification_mail(subject, to_email, message):
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [to_email, ]
    send_mail(subject,message,from_email,recipient_list,fail_silently=False)
    