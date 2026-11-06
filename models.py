from django.contrib.gis.db import models


class Station(models.Model):
    """A daladala stage / stop. Riders know these by name, so aliases matter."""
    name = models.CharField(max_length=100)
    location = models.PointField(geography=True, srid=4326)
    ward = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name


class StationAlias(models.Model):
    """Other names people use: Swahili spellings, landmarks, old names."""
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="aliases")
    alias = models.CharField(max_length=100)

    class Meta:
        indexes = [models.Index(fields=["alias"])]

    def __str__(self):
        return f"{self.alias} → {self.station.name}"


class Route(models.Model):
    """
    ONE DIRECTION of a daladala line. Kimara→Posta and Posta→Kimara are two
    Route rows. Boring, but it handles one-way streets and different fares
    per direction without special cases.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True, help_text="Painted route code/number, if any")
    origin = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="origin_routes")
    destination = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="destination_routes")
    direction = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}: {self.origin} → {self.destination}"


class RouteStop(models.Model):
    """
    A station at a position along a route.
    fare_stage is what makes fares work: fares depend on how many fare stages
    you cross, not on kilometres. Neighbouring stops often share a stage.
    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="stops")
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_stops")
    sequence = models.PositiveIntegerField()
    fare_stage = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["route", "sequence"]
        constraints = [
            models.UniqueConstraint(fields=["route", "sequence"], name="uniq_route_sequence"),
        ]

    def __str__(self):
        return f"{self.route.name} - {self.sequence}. {self.station.name}"


class TransferPoint(models.Model):
    """
    MANUAL override only. The routing engine finds transfers by itself
    (shared station, or another station within walking distance).
    Use this to add a transfer it cannot know about, or to forbid a bad one.
    """
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="transfer_points")
    route_a = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="transfer_points_as_a")
    route_b = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="transfer_points_as_b")
    walking_distance_meters = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~models.Q(route_a=models.F("route_b")), name="transfer_distinct_routes"),
        ]

    def __str__(self):
        return f"{self.station.name}: {self.route_a.name} ↔ {self.route_b.name}"
