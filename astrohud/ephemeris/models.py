"""Models for working with ephemeris"""

from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Tuple
import os

import swisseph as swe

from astrohud._base.models import BaseMatchable
from astrohud._base.models import BaseSplitter
from astrohud._base.models import Splitter2D
from astrohud.ephemeris.enums import House
from astrohud.ephemeris.enums import Planet
from astrohud.ephemeris.enums import Sign
from astrohud.ephemeris.enums import Zodiac


def init_ephe():
    dirname = os.path.dirname(__file__)
    ephe_path = os.path.join(dirname, '../../submodules/swisseph/ephe')
    swe.set_ephe_path(ephe_path)


@dataclass
class EpheSettings:
    """Settings for ephemeris calculation"""

    orb_limit: float
    location: Tuple[float, float]
    zodiac: Zodiac
    house_sys: bytes


class EpheDate:
    ut: float
    obliquity: float

    def __init__(self, date: datetime):
        assert date.tzinfo == timezone.utc
        date_tup = date.timetuple()[:6]
        _, self.ut = swe.utc_to_jd(*date_tup, swe.GREG_CAL)
        
        results, _ = swe.calc_ut(self.ut, swe.ECL_NUT, 0)
        self.obliquity = results[0]


class SignPosition(BaseMatchable):
    """The position within a single sign"""

    abs_angle: float    # degrees from start
    sign: Sign          # Sign
    declination: float  # degrees from ecliptic
    speed: float        # degrees / day
    house: House        # House

    def __init__(
        self,
        signs: BaseSplitter[Sign],
        houses: BaseSplitter[House],
        ra: float,
        dec: float = 0,
        speed: float = 0
    ):
        """Constructor"""
        self.abs_angle = ra
        self.declination = dec
        self.speed = speed
        self.sign = signs.split(ra, dec)
        self.house = houses.split(ra, dec)

    @classmethod
    def from_planet(
        cls,
        ut: float,
        planet: Planet,
        zodiac: Zodiac,
        signs: BaseSplitter[Sign],
        houses: BaseSplitter[House]
    ):
        """Construct for a planet"""
        flags = swe.FLG_SPEED
        if zodiac == Zodiac.SIDEREAL:
            flags |= swe.FLG_SIDEREAL
        results, flags = swe.calc_ut(ut, planet.value, flags=flags)
        ra = results[0]
        dec = results[1]
        speed = results[3]
        return cls(signs, houses, ra, dec, speed)


class HouseSplitter(Splitter2D[House]):
    def __init__(self, ut: float, settings: EpheSettings):
        """Constructor"""
        super().__init__()
        flag_args = dict()
        if settings.zodiac == Zodiac.SIDEREAL:
            flag_args['flags'] = swe.FLG_SIDEREAL
        cusps, angles = swe.houses_ex(
            ut,
            settings.location[0],
            settings.location[1],
            hsys=settings.house_sys,
            **flag_args
        )

        self.ascendant_ra = angles[0]

        self.ring = {c: House(i + 1) for i, c in enumerate(cusps)}

    def get_ascendant(self, signs: BaseSplitter[Sign]) -> SignPosition:
        return SignPosition(signs, self, self.ascendant_ra)
