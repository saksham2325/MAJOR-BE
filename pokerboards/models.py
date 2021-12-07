from datetime import timedelta

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from commons import models as commons_models
from poker_backend import settings
from pokerboards import constant as pokerboards_constant


class Pokerboard(commons_models.Timestamp):
    ESTIMATE_TYPE = [
        (pokerboards_constant.FIBONACCI, 'Fibonacci'),
        (pokerboards_constant.ODD, 'Odd'),
        (pokerboards_constant.EVEN, 'Even'),
        (pokerboards_constant.SERIAL, 'Serial'),
        (pokerboards_constant.CUSTOM, 'Custom')
    ]

    name = models.CharField(
        max_length=pokerboards_constant.POKERBOARD_NAME_MAX_LENGTH, unique=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    estimate_type = models.PositiveSmallIntegerField(
        choices=ESTIMATE_TYPE, default=pokerboards_constant.FIBONACCI)
    deck = models.DecimalField(max_digits=pokerboards_constant.ESTIMATE_MAX_DIGITS, decimal_places=pokerboards_constant.ESTIMATE_DECIMAL_PLACES, validators=[
                               MaxValueValidator(pokerboards_constant.ESTIMATE_MAX_VALUE), MinValueValidator(pokerboards_constant.ESTIMATE_MIN_VALUE)])
    duration = models.DurationField(default=timedelta(
        minutes=pokerboards_constant.TIMER_DEFAULT_MINUTES))

    def __str__(self):
        return self.name


class PokerboardInvitation(commons_models.Timestamp, commons_models.Invitation):
    ROLE = [
        (pokerboards_constant.PLAYER, 'Player'),
        (pokerboards_constant.SPECTATOR, 'Spectator')
    ]

    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    role = ArrayField(models.CharField(
        choices=ROLE, default=pokerboards_constant.PLAYER))

    def __str__(self):
        if(self.user):
            return "{} -> {} {}".format(self.pokerboard.name, self.user.first_name, self.user.last_name)
        return "{} -> {}".format(self.pokerboard.name, self.new_user_name)


class UserPokerboard(commons_models.Timestamp):
    ROLE = [
        (pokerboards_constant.PLAYER, 'Player'),
        (pokerboards_constant.SPECTATOR, 'Spectator')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    role = ArrayField(models.CharField(
        choices=ROLE, default=pokerboards_constant.PLAYER))

    class Meta:
        unique_together = ('user', 'pokerboard',)

    def __str__(self):
        return "{} {} -> {}".format(self.user.first_name, self.user.last_name, self.pokerboard.name)


class Ticket(commons_models.Timestamp):
    STATUS = [
        (pokerboards_constant.TODO, 'ToDo'),
        (pokerboards_constant.INPROGRESS, 'InProgress'),
        (pokerboards_constant.COMPLETED, 'Completed')
    ]

    ticket_id = models.PositiveIntegerField(unique=True)
    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    final_estimate = models.DecimalField(max_digits=pokerboards_constant.ESTIMATE_MAX_DIGITS, decimal_places=pokerboards_constant.ESTIMATE_DECIMAL_PLACES, validators=[
                                         MaxValueValidator(pokerboards_constant.ESTIMATE_MAX_VALUE), MinValueValidator(pokerboards_constant.ESTIMATE_MIN_VALUE)], null=True)
    status = models.PositiveSmallIntegerField(
        choices=STATUS, default=pokerboards_constant.TODO)

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
