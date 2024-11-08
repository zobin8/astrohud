"""Models for horoscopes"""

from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Tuple

from astrohud.lib._base.models import BaseMatchable
from astrohud.lib._base.models import BaseSplitter
from astrohud.lib.constellations.models import SignSplitter
from astrohud.lib.ephemeris.enums import House
from astrohud.lib.ephemeris.enums import Planet
from astrohud.lib.ephemeris.enums import Sign
from astrohud.lib.ephemeris.enums import Zodiac
from astrohud.lib.ephemeris.models import EpheDate
from astrohud.lib.ephemeris.models import EpheSettings
from astrohud.lib.ephemeris.models import HouseSplitter
from astrohud.lib.ephemeris.models import SignPosition
from astrohud.lib.horoscope.const import ASPECT_DEGREES
from astrohud.lib.horoscope.const import ELEMENT_ASSOCIATION
from astrohud.lib.horoscope.const import ESSENTIAL_SCORE
from astrohud.lib.horoscope.const import EXALTATIONS
from astrohud.lib.horoscope.const import RETROGRADE_SCORE
from astrohud.lib.horoscope.const import RULERS
from astrohud.lib.horoscope.const import TRIPLICITIES
from astrohud.lib.horoscope.const import TRIPLICITY_TIME
from astrohud.lib.horoscope.enums import Aspect
from astrohud.lib.horoscope.enums import Dignity
from astrohud.lib.horoscope.enums import Dignity


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
    positive_score: float = 0
    negative_score: float = 0

    def __init__(self, ed: EpheDate, planet: Planet, zodiac: Zodiac, signs: BaseSplitter[Sign], houses: BaseSplitter[House]):
        self.planet = planet
        self.position = SignPosition.from_planet(ed.ut, planet, zodiac, signs, houses)
        self.dignity = self._get_planet_dignity(signs)
        self.retrograde = self.position.speed < 0
        self._assign_scores()

    def add_aspect(self, aspect: Aspect):
        self._add_scores(ESSENTIAL_SCORE[aspect])

    def _assign_scores(self) -> Tuple[float, float]:
        scores = list(ESSENTIAL_SCORE[self.dignity])
        if self.retrograde:
            scores += [RETROGRADE_SCORE]
        self._add_scores(scores)

    def _add_scores(self, scores: List[float]):
        for score in scores:
            if score > 0:
                self.positive_score += score
            if score < 0:
                self.negative_score += score

    def _get_planet_dignity(self, signs: BaseSplitter[Sign]) -> Dignity:
        sign = self.position.sign
        house = self.position.house
        opposite = signs.split(self.position.abs_angle + 180, -self.position.declination)
        triplicity = None
        if sign in ELEMENT_ASSOCIATION:
            triplicity = TRIPLICITIES[ELEMENT_ASSOCIATION[sign]][TRIPLICITY_TIME[house]]

        if RULERS[sign] == self.planet:
            return Dignity.DIGNITY
        if RULERS[opposite] == self.planet:
            return Dignity.DETRIMENT
        if self.planet in EXALTATIONS:
            if EXALTATIONS[self.planet][0] == sign:
                return Dignity.EXALTATION
            if EXALTATIONS[self.planet][0] == opposite:
                return Dignity.FALL
        if self.planet == triplicity:
            return Dignity.TRIPLICITY
        return Dignity.NORMAL
    

class AspectHoroscope(BaseMatchable):
    """The horoscope for a single aspect"""

    aspect: Aspect
    orb: float

    def __init__(self, p1: PlanetHoroscope, p2: PlanetHoroscope, settings: EpheSettings):
        angle = abs(p1.position.abs_angle - p2.position.abs_angle)
        if angle > 180:
            angle = 360 - angle

        for aspect, target_angle in ASPECT_DEGREES.items():
            orb = abs(angle - target_angle)
            limit = settings.orb_limit
            if aspect == Aspect.CONJUNCTION:
                limit = settings.conjunction_limit

            if orb < limit:
                self.aspect = aspect
                self.orb = orb
                p1.add_aspect(aspect)
                p2.add_aspect(aspect)
                return
            
        self.aspect = Aspect.NONE
        self.orb = 0


class Horoscope(BaseMatchable):
    """Complete horoscope summary"""

    planets: Dict[Planet, PlanetHoroscope]
    ascending: SignPosition
    signs: Dict[Sign, Tuple[float, float]]
    houses: Dict[House, float]
    aspects: Dict[PlanetTuple, AspectHoroscope]

    house_splitter: HouseSplitter
    sign_splitter: SignSplitter

    def __init__(self, ed: EpheDate, settings: EpheSettings):
        self.sign_splitter = SignSplitter(ed.obliquity, settings.zodiac)
        self.house_splitter = HouseSplitter(ed.ut, settings)

        self.planets = dict()
        important_signs = dict()
        for planet in list(Planet):
            self.planets[planet] = PlanetHoroscope(
                ed,
                planet,
                settings.zodiac,
                self.sign_splitter,
                self.house_splitter
            )
            pos = self.planets[planet].position
            important_signs[pos.sign] = pos.declination
        important_signs.update({s: 0 for s in self.sign_splitter.ring[0].ring.values()})

        self._get_all_aspects(settings)

        self.ascending = self.house_splitter.get_ascendant(self.sign_splitter)
        self.houses = {v: k for k, v in self.house_splitter.ring.items()}
        
        self.signs = dict()
        for sign, dec in important_signs.items():
            self.signs[sign] = self.sign_splitter.get_ra_limits(sign, dec)
    
    def _get_all_aspects(self, settings: EpheSettings) -> Dict[PlanetTuple, AspectHoroscope]:
        self.aspects = dict()
        for p1, ph1 in self.planets.items():
            for p2, ph2 in self.planets.items():
                if p1.value >= p2.value:
                    continue
                aspect = AspectHoroscope(ph1, ph2, settings)
                if aspect.aspect != Aspect.NONE:
                    self.aspects[PlanetTuple(p1, p2)] = aspect