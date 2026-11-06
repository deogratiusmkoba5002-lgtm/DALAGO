from django.contrib import admin
from .models import Station, StationAlias, Route, RouteStop, TransferPoint


class StationAliasInline(admin.TabularInline):
    model = StationAlias
    extra = 1


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 0
    autocomplete_fields = ["station"]


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    search_fields = ["name", "aliases__alias", "ward", "district"]
    list_display = ["name", "ward", "district", "active"]
    inlines = [StationAliasInline]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "origin", "destination", "active"]
    autocomplete_fields = ["origin", "destination"]
    inlines = [RouteStopInline]


admin.site.register(TransferPoint)
