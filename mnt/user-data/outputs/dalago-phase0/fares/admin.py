from django.contrib import admin
from .models import FareTable, FareOverride

admin.site.register(FareTable)
admin.site.register(FareOverride)
