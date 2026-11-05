from django.contrib import admin
from .models import Station, Route, RouteStop, StationAlias, TransferPoint

admin.site.register(Station)
admin.site.register(Route)
admin.site.register(RouteStop)
admin.site.register(StationAlias)
admin.site.register(TransferPoint)
