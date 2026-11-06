from django.contrib.gis.geos import Point
from django.test import TestCase

from fares.models import FareTable, FareOverride
from fares.services import fare_between
from transport.models import Station, Route, RouteStop


class FareBetweenTests(TestCase):
    """
    Route: A(stage1) - B(stage1) - C(stage2) - D(stage4)
    Fare table: 0 stages = 400, 1 stage = 500, 3 stages = 800
    """

    @classmethod
    def setUpTestData(cls):
        def station(name, lon):
            return Station.objects.create(name=name, location=Point(lon, -6.8, srid=4326))

        cls.a, cls.b, cls.c, cls.d = (
            station("A", 39.20), station("B", 39.21), station("C", 39.22), station("D", 39.23)
        )
        cls.route = Route.objects.create(name="Test Line", origin=cls.a, destination=cls.d)
        cls.other_route = Route.objects.create(name="Other Line", origin=cls.d, destination=cls.a)

        def stop(st, seq, stage, route=None):
            return RouteStop.objects.create(route=route or cls.route, station=st, sequence=seq, fare_stage=stage)

        cls.sa, cls.sb, cls.sc, cls.sd = stop(cls.a, 1, 1), stop(cls.b, 2, 1), stop(cls.c, 3, 2), stop(cls.d, 4, 4)
        cls.other_stop = stop(cls.d, 1, 1, route=cls.other_route)

        for crossed, amount in [(0, 400), (1, 500), (3, 800)]:
            FareTable.objects.create(route=cls.route, stages_crossed=crossed, amount_tzs=amount)

    def test_same_stage_pays_minimum_fare(self):
        self.assertEqual(fare_between(self.sa, self.sb), 400)

    def test_one_stage_crossed(self):
        self.assertEqual(fare_between(self.sb, self.sc), 500)

    def test_three_stages_crossed(self):
        self.assertEqual(fare_between(self.sa, self.sd), 800)

    def test_missing_exact_row_uses_closest_lower_row(self):
        # B(stage1) -> D(stage4) = 3 stages -> 800; C(stage2) -> D(stage4) = 2 stages -> no row for 2, falls back to 1 stage (500)
        self.assertEqual(fare_between(self.sc, self.sd), 500)

    def test_override_beats_table(self):
        FareOverride.objects.create(board_stop=self.sa, alight_stop=self.sd, amount_tzs=1000)
        self.assertEqual(fare_between(self.sa, self.sd), 1000)

    def test_unknown_fare_returns_none_not_a_guess(self):
        FareTable.objects.filter(route=self.route).delete()
        self.assertIsNone(fare_between(self.sa, self.sd))

    def test_different_routes_rejected(self):
        with self.assertRaises(ValueError):
            fare_between(self.sa, self.other_stop)

    def test_backwards_or_same_stop_rejected(self):
        with self.assertRaises(ValueError):
            fare_between(self.sd, self.sa)
        with self.assertRaises(ValueError):
            fare_between(self.sa, self.sa)
