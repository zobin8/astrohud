"""Models for working with ephemeris"""

from datetime import datetime
from datetime import timezone
import os

import swisseph as swe

from astrohud._base.models import BaseSplitter
from astrohud._base.models import Splitter2D
from astrohud.astro.enums import House
from astrohud.astro.enums import Sign
from astrohud.astro.enums import Zodiac
from astrohud.astro.model import HoroscopeSettings
from astrohud.astro.model import SignPosition


def init_ephe():
    dirname = os.path.dirname(__file__)
    ephe_path = os.path.join(dirname, '../../submodules/swisseph/ephe')
    swe.set_ephe_path(ephe_path)


class EpheDate:
    ut: float
    obliquity: float

    def __init__(self, date: datetime):
        assert date.tzinfo == timezone.utc
        date_tup = date.timetuple()[:6]
        _, self.ut = swe.utc_to_jd(*date_tup, swe.GREG_CAL)
        
        results, _ = swe.calc_ut(self.ut, swe.ECL_NUT, 0)
        self.obliquity = results[0]


class HouseSplitter(Splitter2D[House]):
    def __init__(self, ut: float, settings: HoroscopeSettings):
        """Constructor"""
        super().__init__()
        flag_args = dict()
        if settings.zodiac == Zodiac.SIDEREAL:
            flag_args['flags'] = swe.FLG_SIDEREAL
        cusps, angles = swe.houses_ex(ut, settings.location[0], settings.location[1], hsys=settings.house_sys, **flag_args)

        self.ascendant_ra = angles[0]

        self.ring = {c: House(i + 1) for i, c in enumerate(cusps)}

    def get_ascendant(self, signs: BaseSplitter[Sign]) -> SignPosition:
        return SignPosition(
            abs_angle=self.ascendant_ra,
            sign=signs.split(self.ascendant_ra, 0),
            speed=0,
            declination=0,
            house=House.IDENTITY_1,
        )
