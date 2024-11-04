"""Models for Star chart"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
import math

from astrohud.chart._base.const import IMAGE_PAD
from astrohud.chart._base.const import MAX_RADIUS
from astrohud.chart._base.models import BaseChart
from astrohud.chart._base.models import BaseCoord
from astrohud.chart._base.models import XY
from astrohud.chart.shapes.models import Arc
from astrohud.chart.shapes.models import Circle
from astrohud.chart.shapes.models import Label
from astrohud.chart.shapes.models import Line
from astrohud.lib.ephemeris.enums import House
from astrohud.lib.ephemeris.enums import Planet
from astrohud.lib.ephemeris.enums import Sign
from astrohud.lib.horoscope.enums import Aspect
from astrohud.lib.horoscope.enums import Dignity
from astrohud.lib.horoscope.const import ESSENTIAL_SCORE
from astrohud.lib.horoscope.models import Horoscope



@dataclass(frozen=True)
class StarCoord(BaseCoord):
    """Class for ecliptic coordinates in star chart."""


class StarChart(BaseChart):
    """Standard natal chart designed as an ecliptic wheel"""
    
    asc_angle: float
    horoscope: Horoscope

    def __init__(self, horoscope: Horoscope):
        """Constructor"""
        super().__init__()

        self.asc_angle = horoscope.ascending.abs_angle
        self.horoscope = horoscope

        self._draw_structure()
    
    def convert_coord(self, coord: StarCoord) -> XY:
        """Convert an ecliptic coordinate to chart XY."""

        # Split by house
        house = self.horoscope.house_splitter.split(ra=coord.ra, dec=coord.dec)
        start_deg = self.horoscope.houses[house]
        end_deg = self.horoscope.houses[House((house.value % 12) + 1)]
        if end_deg < start_deg:
            end_deg += 360

        # Sinusoidal projection
        center_deg = (start_deg + end_deg) / 2
        rho = (coord.dec + 90) * MAX_RADIUS / 180
        phi = center_deg + (coord.ra - center_deg) * math.cos(math.radians(coord.dec))

        # Polar to cartesian
        x = rho * math.cos(math.radians(phi))
        y = rho * math.sin(math.radians(phi))

        # Offset
        offset = MAX_RADIUS + IMAGE_PAD
        return XY(x + offset, offset - y)
        

    def _draw_structure(self):
        """Draw the general wheel structure"""

        for house, phi in self.horoscope.houses.items():
            for delta in [-0.1, 0.1]:
                for dec in range(-90, 90, 5):
                    a = StarCoord(ra=phi + delta, dec=dec)
                    b = StarCoord(ra=phi + delta, dec=dec + 5)
                    self.shapes.add(Line(a, b))

        signs = self.horoscope.sign_splitter.constellations.signs
        for sign, points in signs.items():
            next_points = points[1:] + points[:0]
            for p1, p2 in zip(points, next_points):
                a = StarCoord(ra=p1[0] % 360, dec=p1[1])
                b = StarCoord(ra=p2[0] % 360, dec=p2[1])
                #self.shapes.add(Line(a, b))