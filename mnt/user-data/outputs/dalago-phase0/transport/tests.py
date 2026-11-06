from django.contrib.gis.geos import Point
from django.db import IntegrityError, transaction
from django.test import TestCase

from transport.models import Station, Route, RouteStop, TransferPoint


class TransportModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.a = Station.objects.create(name="Mwenge", location=Point(39.2, -6.77, srid=4326))
        cls.b = Station.objects.create(name="Posta", location=Point(39.29, -6.81, srid=4326))
        cls.route = Route.objects.create(name="Mwenge-Posta", origin=cls.a, destination=cls.b)

    def test_stops_come_back_in_sequence_order(self):
        RouteStop.objects.create(route=self.route, station=self.b, sequence=2)
        RouteStop.objects.create(route=self.route, station=self.a, sequence=1)
        names = [s.station.name for s in self.route.stops.all()]
        self.assertEqual(names, ["Mwenge", "Posta"])

    def test_duplicate_sequence_on_a_route_is_rejected(self):
        RouteStop.objects.create(route=self.route, station=self.a, sequence=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            RouteStop.objects.create(route=self.route, station=self.b, sequence=1)

    def test_transfer_between_a_route_and_itself_is_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            TransferPoint.objects.create(station=self.a, route_a=self.route, route_b=self.route)

    def test_station_is_geographic_point(self):
        self.a.refresh_from_db()
        self.assertEqual(self.a.location.srid, 4326)
