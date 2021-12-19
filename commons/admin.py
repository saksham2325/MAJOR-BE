from django.contrib import admin

from commons import models as common_models


admin.site.register(common_models.EmailVerification)
