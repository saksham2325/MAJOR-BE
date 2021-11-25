from django.contrib import admin
from accounts import models

from accounts import models


admin.site.register(models.User)
admin.site.register(models.Group)
admin.site.register(models.UserGroup)
admin.site.register(models.GroupInvitation)
admin.site.register(models.UserJiraToken)
