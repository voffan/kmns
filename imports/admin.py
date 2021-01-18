from django.contrib import admin
from imports import models

# Register your models here.
admin.site.register(models.ListTemplate)
admin.site.register(models.TableTemplate)
#admin.site.register(models.TemplateIndicators)
admin.site.register(models.ImportResult)
