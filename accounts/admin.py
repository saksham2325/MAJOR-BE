from django.contrib import admin

from accounts import models as account_models


admin.site.register(account_models.User)
admin.site.register(account_models.Group)
admin.site.register(account_models.GroupInvitation)
admin.site.register(account_models.UserJiraToken)
