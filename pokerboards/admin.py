from django.contrib import admin

from pokerboards import models as pokerboards_models


admin.site.register(pokerboards_models.Pokerboard)
admin.site.register(pokerboards_models.PokerboardInvitation)
admin.site.register(pokerboards_models.UserPokerboard)
admin.site.register(pokerboards_models.Ticket)
admin.site.register(pokerboards_models.PlayerTicket)
