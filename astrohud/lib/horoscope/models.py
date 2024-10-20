from dataclasses import dataclass
from typing import Dict

from astrohud.lib._base.models import BaseMatchable
from astrohud.lib._base.models import BaseSplitter
from astrohud.lib.horoscope.const import ASPECT_DEGREES
from astrohud.lib.horoscope.const import EXALTATIONS
from astrohud.lib.horoscope.const import RULERS
from astrohud.lib.horoscope.enums import Aspect
from astrohud.lib.horoscope.enums import Dignity
from astrohud.lib.horoscope.enums import Dignity
from astrohud.lib.ephemeris.enums import House
from astrohud.lib.ephemeris.enums import Planet
from astrohud.lib.ephemeris.enums import Sign
from astrohud.lib.ephemeris.enums import Zodiac
from astrohud.lib.constellations.models import SignSplitter
from astrohud.lib.ephemeris.models import EpheDate
from astrohud.lib.ephemeris.models import HouseSplitter
from astrohud.lib.ephemeris.models import EpheSettings
from astrohud.lib.ephemeris.models import SignPosition


@dataclass(frozen=True)
class PlanetTuple(BaseMatchable):
    """A key type with two planets"""

    planet1: Planet
    planet2: Planet

    def __post_init__(self):
        if self.planet2.value < self.planet1.value:
            self.planet1, self.planet2 = self.planet2, self.planet1

    def to_json(self):
        """Turn self into a matchable json type. Override."""
        return f'{self.planet1.name},{self.planet2.name}'


class PlanetHoroscope(BaseMatchable):
    """Horoscope summary for a single planet"""

    planet: Planet
    position: SignPosition
    dignity: Dignity
    retrograde: bool

    def __init__(self, ed: EpheDate, planet: Planet, zodiac: Zodiac, signs: BaseSplitter[Sign], houses: BaseSplitter[House]):
        self.planet = planet
        self.position = SignPosition.from_planet(ed.ut, planet, zodiac, signs, houses)
        self.dignity = self._get_planet_dignity(signs)
        self.retrograde = self.position.speed < 0

    def _get_planet_dignity(self, signs: BaseSplitter[Sign]) -> Dignity:
        sign = self.position.sign
        opposite = signs.split(self.position.abs_angle + 180, -self.position.declination)
        if RULERS[sign] == self.planet:
            return Dignity.DIGNITY
        if RULERS[opposite] == self.planet:
            return Dignity.DETRIMENT
        if self.planet in EXALTATIONS:
            if EXALTATIONS[self.planet][0] == sign:
                return Dignity.EXALTATION
            if EXALTATIONS[self.planet][0] == opposite:
                return Dignity.FALL
        return Dignity.NORMAL
    

class AspectHoroscope(BaseMatchable):
    """The horoscope for a single aspect"""

    aspect: Aspect
    orb: float

    def __init__(self, p1: PlanetHoroscope, p2: PlanetHoroscope, orb_limit=float):
        angle = abs(p1.position.abs_angle - p2.position.abs_angle)
        if angle > 180:
            angle = 360 - angle

        for aspect, target_angle in ASPECT_DEGREES.items():
            orb = abs(angle - target_angle)
            if orb < orb_limit:
                self.aspect = aspect
                self.orb = orb
                return
            
        self.aspect = Aspect.NONE
        self.orb = 0


class Horoscope(BaseMatchable):
    """Complete horoscope summary"""

    planets: Dict[Planet, PlanetHoroscope]
    ascending: SignPosition
    signs: Dict[Sign, float]
    houses: Dict[House, float]
    aspects: Dict[PlanetTuple, AspectHoroscope]

    def __init__(self, ed: EpheDate, settings: EpheSettings):
        signs = SignSplitter(ed.obliquity, settings.zodiac)
        houses = HouseSplitter(ed.ut, settings)

        self.planets = dict()
        for planet in list(Planet):
            self.planets[planet] = PlanetHoroscope(
                ed,
                planet,
                settings.zodiac,
                signs,
                houses
            )

        self._get_all_aspects(settings.orb_limit)

        self.ascending = houses.get_ascendant(signs)
        self.houses = {v: k for k, v in houses.ring.items()}
        self.signs = {v: k for k, v in signs.ring[0].ring.items()}
    
    def _get_all_aspects(self, orb_limit: float) -> Dict[PlanetTuple, AspectHoroscope]:
        self.aspects = dict()
        for p1, ph1 in self.planets.items():
            for p2, ph2 in self.planets.items():
                if p1.value >= p2.value:
                    continue
                aspect = AspectHoroscope(ph1, ph2, orb_limit)
                if aspect.aspect != Aspect.NONE:
                    self.aspects[PlanetTuple(p1, p2)] = aspect
