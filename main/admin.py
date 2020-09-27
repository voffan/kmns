from django.contrib import admin
from main import models
# Register your models here.
admin.site.register(models.Table)
admin.site.register(models.Tag)
admin.site.register(models.Row)
admin.site.register(models.Column)
admin.site.register(models.Cell)
admin.site.register(models.CellValue)