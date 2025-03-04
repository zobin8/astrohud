"""Models for working with ephemeris"""

from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Tuple
import os

import swisseph as swe

from astrohud.lib._base.models import BaseSplitter
from astrohud.lib._base.models import Splitter2D
from astrohud.lib.ephemeris.enums import House
from astrohud.lib.ephemeris.enums import Planet
from astrohud.lib.ephemeris.enums import Sign
from astrohud.lib.ephemeris.enums import Zodiac
from astrohud.lib.math.models import Angle
from astrohud.lib.math.models import AngleSegment


def init_ephe():
    dirname = os.path.dirname(__file__)
    ephe_path = os.path.join(dirname, '../../submodules/swisseph/ephe')
    swe.set_ephe_path(ephe_path)


@dataclass
class EpheSettings:
    """Settings for ephemeris calculation"""

    orb_limit: float
    conjunction_limit: float
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


class SignPosition:
    """The position within a single sign"""

    abs_angle: float    # degrees from start
    sign: Sign          # Sign
    face: int           # Face in sign
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

        self.face = self._get_face(signs)

    def _get_face(self, signs: BaseSplitter[Sign]) -> int:
        """Get the face of the sign region"""
        sign_limits = signs.get_ra_limits(self.sign, self.declination)
        face_length = sign_limits.length() / 3
        for face_index in range(3):
            face_start = face_index * face_length + sign_limits.a1.standard_value()
            face = AngleSegment(face_start, face_start + face_length)
            if face.check_collision(Angle(self.abs_angle), 0):
                return face_index

        return -1

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

        # TODO: Fix combination of W/N House Sys with IAU/Stellar zodiac

        self.ascendant_ra = angles[0]
        self.midheaven_ra = angles[1]

        next_cusps = cusps[1:] + cusps[:1]
        houses = [House(i + 1) for i in range(len(cusps))]
        self.ring = {AngleSegment(c1, c2): h for h, c1, c2 in zip(houses, cusps, next_cusps)}

    def get_ascmc(self, signs: BaseSplitter[Sign]) -> Tuple[SignPosition, SignPosition]:
        asc = SignPosition(signs, self, self.ascendant_ra)
        mc = SignPosition(signs, self, self.midheaven_ra)
        return asc, mc
