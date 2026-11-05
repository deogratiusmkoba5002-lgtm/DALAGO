from django.contrib.gis.db import models

class Station(models.Model):
  name = models.CharField(max_length=100)
  location = models.PointField(
     geography=True,
     srid=4326
  )
  ward = models.CharField(max_length=100 , blank=True)
  district = models.CharField(max_length=100 , blank=True)
  active = models.BooleanField(default=True)

  def __str__(self):
    return self.name

class Route(models.Model):
  name = models.CharField(max_length=100)
  origin = models.ForeignKey(
    Station,
    on_delete=models.PROTECT,
    related_name="origin_routes"
  )
  destination = models.ForeignKey(
    Station,
    on_delete=models.PROTECT,
    related_name="destination_routes"
  )
  direction = models.CharField(max_length=50 , blank=True)
  active = models.BooleanField(default=True)

  def __str__(self):
    return f"{self.name}: {self.origin} → {self.destination}"

class RouteStop(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="stops"
    )
    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="route_stops"
    )
    sequence = models.PositiveIntegerField()

    class Meta:
        ordering = ["sequence"]
        unique_together = ["route", "sequence"]

    def __str__(self):
        return f"{self.route.name} - {self.sequence}. {self.station.name}"

class StationAlias(models.Model):
    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="aliases"
    )
    alias = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.alias} → {self.station.name}"

class TransferPoint(models.Model):
    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="transfer_points"
    )
    route_a = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="transfer_points_as_a"
    )
    route_b = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="transfer_points_as_b"
    )
    walking_distance_meters = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.station.name}: {self.route_a.name} ↔ {self.route_b.name}"