from django.contrib import admin
from . import models
# Register your models here.
admin.site.register([models.Applicants,models.Limit,models.DataEntryPeriod])

  