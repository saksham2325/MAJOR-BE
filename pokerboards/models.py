from datetime import timedelta

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from commons import models as commons_models
from poker_backend import settings
from pokerboards import constant as pokerboards_constant


class Pokerboard(commons_models.Timestamp):
    FIBONACCI = 0
    ODD = 1
    EVEN = 2
    SERIAL = 3
    CUSTOM = 4

    ESTIMATE_TYPE = [
        (FIBONACCI, 'Fibonacci'),
        (ODD, 'Odd'),
        (EVEN, 'Even'),
        (SERIAL, 'Serial'),
        (CUSTOM, 'Custom')
    ]

    name = models.CharField(
        max_length=pokerboards_constant.POKERBOARD_NAME_MAX_LENGTH, unique=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    estimate_type = models.PositiveSmallIntegerField(
        choices=ESTIMATE_TYPE, default=FIBONACCI)
    deck = models.DecimalField(max_digits=pokerboards_constant.ESTIMATE_MAX_DIGITS, decimal_places=pokerboards_constant.ESTIMATE_DECIMAL_PLACES, validators=[
                               MaxValueValidator(pokerboards_constant.ESTIMATE_MAX_VALUE), MinValueValidator(pokerboards_constant.ESTIMATE_MIN_VALUE)])
    duration = models.DurationField(default=timedelta(
        minutes=pokerboards_constant.TIMER_DEFAULT_MINUTES))

    def __str__(self):
        return self.name


class PokerboardInvitation(commons_models.Invitation):
    PLAYER = 0
    SPECTATOR = 1

    ROLE = [
        (PLAYER, 'Player'),
        (SPECTATOR, 'Spectator')
    ]

    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    role = ArrayField(models.CharField(
        choices=ROLE, default=PLAYER))

    def __str__(self):
        if(self.user):
            return "{} -> {} {}".format(self.pokerboard.name, self.user.first_name, self.user.last_name)
        return "{} -> {}".format(self.pokerboard.name, self.new_user_name)


class UserPokerboard(commons_models.Timestamp):
    PLAYER = 0
    SPECTATOR = 1

    ROLE = [
        (PLAYER, 'Player'),
        (SPECTATOR, 'Spectator')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    role = ArrayField(models.CharField(
        choices=ROLE, default=PLAYER))

    class Meta:
        unique_together = ('user', 'pokerboard',)

    def __str__(self):
        return "{} {} -> {}".format(self.user.first_name, self.user.last_name, self.pokerboard.name)


class Ticket(commons_models.Timestamp):
    TODO = 0
    INPROGRESS = 1
    COMPLETED = 2

    STATUS = [
        (TODO, 'ToDo'),
        (INPROGRESS, 'InProgress'),
        (COMPLETED, 'Completed')
    ]

    ticket_id = models.PositiveIntegerField(unique=True)
    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    final_estimate = models.DecimalField(max_digits=pokerboards_constant.ESTIMATE_MAX_DIGITS, decimal_places=pokerboards_constant.ESTIMATE_DECIMAL_PLACES, validators=[
                                         MaxValueValidator(pokerboards_constant.ESTIMATE_MAX_VALUE), MinValueValidator(pokerboards_constant.ESTIMATE_MIN_VALUE)], null=True)
    status = models.PositiveSmallIntegerField(
        choices=STATUS, default=TODO)

    def __str__(self):
        return self.ticket_id


class PlayerTicket(commons_models.Timestamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    estimate = models.DecimalField(max_digits=pokerboards_constant.ESTIMATE_MAX_DIGITS, decimal_places=pokerboards_constant.ESTIMATE_DECIMAL_PLACES, validators=[
                                   MaxValueValidator(pokerboards_constant.ESTIMATE_MAX_VALUE), MinValueValidator(pokerboards_constant.ESTIMATE_MIN_VALUE)], null=True)
    time_taken = models.DurationField(default=timedelta(
        minutes=pokerboards_constant.TIMER_DEFAULT_MINUTES))

    class Meta:
        unique_together = ('user', 'ticket',)

    def __str__(self):
        return "{} {} -> {}".format(self.user.first_name, self.user.last_name, self.ticket.ticket_id)
