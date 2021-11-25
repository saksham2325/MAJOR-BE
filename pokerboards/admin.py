from django.contrib import admin

from pokerboards.models import PlayerTicket, Pokerboard, PokerboardInvitation, Ticket, UserPokerboard


admin.site.register(Pokerboard)
admin.site.register(PokerboardInvitation)
admin.site.register(UserPokerboard)
admin.site.register(Ticket)
admin.site.register(PlayerTicket)
