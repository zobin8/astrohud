"""Models for constellations."""

from collections import defaultdict
from typing import Dict
from typing import List
from typing import Tuple
import math
import os

import pandas as pd

from astrohud.lib._base.models import Splitter2D
from astrohud.lib._base.models import Splitter3D
from astrohud.lib.ephemeris.enums import Sign
from astrohud.lib.ephemeris.enums import Zodiac


CONSTELLATIONS: Dict[Sign, List[Tuple[float, float]]] = defaultdict(list)


def init_constellations():
    dirname = os.path.dirname(__file__)

    constellation_path = os.path.join(dirname, '../../data/constellations_all.csv')
    df = pd.read_csv(constellation_path)
    df['Angle'] = ((df.Seconds / 60 + df.Minutes) / 60 + df.Hours) * 15
    df['Sign'] = df.Sign.apply(lambda n: getattr(Sign, n.upper()))
    for _, row in df.iterrows():
        CONSTELLATIONS[row.Sign].append((row.Angle, row.Declination))


class Constellations:
    signs: Dict[Sign, List[Tuple[float, float]]]
    obliquity: float

    def __init__(self, obliquity: float):
        """Constructor"""
        self.signs = dict()
        self.obliquity = obliquity
        for sign, celestial_points in CONSTELLATIONS.items():
            points = [self._celestial_to_ecliptic(x, y) for x, y in celestial_points]
            self.signs[sign] = points

    def _celestial_to_ecliptic(self, celestial_x: float, celestial_y: float) -> Tuple[float, float]:
        """Convert celestial coordinates (constellations) to ecliptic coordinates
        
        Formula derived by:
        1. Converting to Cartesian (x=cosa cosb, y=sina cosb, z=sinb)
        2. Rotating across X axis
        3. Converting back to Spherical
        """

        cos_cx = math.cos(math.radians(celestial_x))
        sin_cx = math.sin(math.radians(celestial_x))
        cos_cy = math.cos(math.radians(celestial_y))
        sin_cy = math.sin(math.radians(celestial_y))
        cos_ob = math.cos(-math.radians(self.obliquity))
        sin_ob = math.sin(-math.radians(self.obliquity))

        sin_ey = sin_ob * sin_cx * cos_cy + cos_ob * sin_cy
        ey = math.asin(sin_ey)

        cos_ex = cos_cx * cos_cy / math.cos(ey)
        ex_pos = cos_ob * sin_cx * cos_cy
        ex_neg = sin_ob * sin_cy
        ex = math.acos(cos_ex)
        if ex_neg > ex_pos:
            ex *= -1
    
        return math.degrees(ex), math.degrees(ey)


class SignSplitter(Splitter3D[Sign]):
    constellations: Constellations

    def __init__(self, obliquity: float, zodiac: Zodiac):
        """Constructor"""
        super().__init__()
        self.constellations = Constellations(obliquity)

        if zodiac == Zodiac.IAU:
            self.ring[0] = self._get_iau_ring(0)
        elif zodiac == Zodiac.PLANETARIUM:
            for declination in range(-88, 90, 2):
                ring = self._get_iau_ring(declination)
                self.ring[declination] = ring
        else:
            ring = Splitter2D[Sign]()
            for i in range(12):
                ring.ring[i * 30] = Sign(i)

            self.ring[0] = ring

    def _get_iau_ring(self, declination: float) -> Splitter2D[Sign]:
        out = Splitter2D[Sign]()
        for sign, points in self.constellations.signs.items():
            next_points = points[1:] + points[:0]
            cusp = None
            # ZTODO: 2024-11-28T16:31:00
            for pt1, pt2 in zip(points, next_points):
                if (pt1[1] > declination) != (pt2[1] > declination):
                    m = (pt1[1] - pt2[1]) / (pt1[0] - pt2[0])
                    x = pt1[0] - pt1[1] / m
                    x += declination / m
                    if cusp is not None:
                        while x - cusp > 180:
                            x -= 360
                        while cusp - x > 180:
                            x += 360
                        if x > cusp:
                            break
                    cusp = x
            if cusp is not None:
                out.ring[cusp] = sign

        return out