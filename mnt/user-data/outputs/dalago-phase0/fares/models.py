from django.db import models
from transport.models import Route, RouteStop


class FareTable(models.Model):
    """
    Price for crossing N fare stages on a route.
    stages_crossed = 0 means boarding and alighting inside the same stage
    (the minimum fare).
    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="fare_table")
    stages_crossed = models.PositiveSmallIntegerField()
    amount_tzs = models.PositiveIntegerField()
    source = models.CharField(max_length=100, blank=True, help_text="LATRA table, driver, rider report...")
    verified_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["route", "stages_crossed"]
        constraints = [
            models.UniqueConstraint(fields=["route", "stages_crossed"], name="uniq_route_stages"),
        ]

    def __str__(self):
        return f"{self.route.name}: {self.stages_crossed} stages = {self.amount_tzs} TZS"


class FareOverride(models.Model):
    """The exceptions. Because someone always charges differently between two specific stops."""
    board_stop = models.ForeignKey(RouteStop, on_delete=models.CASCADE, related_name="+")
    alight_stop = models.ForeignKey(RouteStop, on_delete=models.CASCADE, related_name="+")
    amount_tzs = models.PositiveIntegerField()
    source = models.CharField(max_length=100, blank=True)
    verified_at = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["board_stop", "alight_stop"], name="uniq_override_pair"),
        ]

    def __str__(self):
        return f"{self.board_stop} → {self.alight_stop}: {self.amount_tzs} TZS"
