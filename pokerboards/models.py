from datetime import timedelta

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from commons import Invitation, Timestamp
from poker_backend import settings
from pokerboards import constant as pc


class Pokerboard(Timestamp):
    name = models.CharField(max_length=pc.POKERBOARD_NAME_MAX_LENGTH, unique=True)
    manager	= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    estimate_type = models.PositiveSmallIntegerField(choices=pc.ESTIMATE_TYPE, default=pc.ESTIMATE_TYPE["fibonacci"])
    deck = models.DecimalField(max_digits=pc.ESTIMATE_MAX_DIGITS, decimal_places=pc.ESTIMATE_DECIMAL_PLACES, validators=[MaxValueValidator(pc.ESTIMATE_MAX_VALUE), MinValueValidator(pc.ESTIMATE_MIN_VALUE)])
    duration = models.DurationField(default=timedelta(minutes=pc.TIMER_DEFAULT_MINUTES))


class PokerboardInvitation(Timestamp, Invitation):
    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    role = ArrayField(models.CharField(choices=pc.ROLE, default=pc.ROLE['player']))


class UserPokerboard(Timestamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    role = ArrayField(models.CharField(choices=pc.ROLE, default=pc.ROLE['player']))

    class Meta:
        unique_together = ('user', 'pokerboard',)


class Ticket(Timestamp):
    ticket_id = models.PositiveIntegerField(unique=True)
    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    final_estimate = models.DecimalField(max_digits=pc.ESTIMATE_MAX_DIGITS, decimal_places=pc.ESTIMATE_DECIMAL_PLACES, validators=[MaxValueValidator(pc.ESTIMATE_MAX_VALUE), MinValueValidator(pc.ESTIMATE_MIN_VALUE)], null=True)
    status = models.PositiveSmallIntegerField(choices=pc.STATUS, default=pc.STATUS['ToDo'])

    class Meta:
        unique_together = ('ticket_id', 'pokerboard',)


class PlayerTicket(Timestamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    estimate = models.DecimalField(max_digits=pc.ESTIMATE_MAX_DIGITS, decimal_places=pc.ESTIMATE_DECIMAL_PLACES, validators=[MaxValueValidator(pc.ESTIMATE_MAX_VALUE), MinValueValidator(pc.ESTIMATE_MIN_VALUE)], null=True)
    time_taken = models.DurationField(default=timedelta(minutes=pc.TIMER_DEFAULT_MINUTES))

    class Meta:
        unique_together = ('user', 'ticket',)
