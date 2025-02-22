"""Models for horoscopes"""

from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

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
from astrohud.lib.horoscope.const import DECANS
from astrohud.lib.horoscope.const import ELEMENT_ASSOCIATION
from astrohud.lib.horoscope.const import ESSENTIAL_SCORE
from astrohud.lib.horoscope.const import EXALTATIONS
from astrohud.lib.horoscope.const import RETROGRADE_SCORE
from astrohud.lib.horoscope.const import RULERS
from astrohud.lib.horoscope.const import TRIPLICITIES
from astrohud.lib.horoscope.const import TRIPLICITY_TIME
from astrohud.lib.horoscope.enums import Aspect
from astrohud.lib.horoscope.enums import Dignity
from astrohud.lib.math.models import Angle
from astrohud.lib.math.models import AngleSegment


@dataclass(frozen=True)
class PlanetTuple:
    """A key type with two planets"""

    planet1: Planet
    planet2: Planet

    def __post_init__(self):
        if self.planet2.value < self.planet1.value:
            self.planet1, self.planet2 = self.planet2, self.planet1

    def __str__(self):
        """Return as string"""
        return f'{self.planet1.name},{self.planet2.name}'


class PlanetHoroscope:
    """Horoscope summary for a single planet"""

    position: SignPosition
    dignity: Dignity
    retrograde: bool
    score: float = 0

    def __init__(self, ed: EpheDate, planet: Planet, zodiac: Zodiac, signs: BaseSplitter[Sign], houses: BaseSplitter[House]):
        """Constructor"""
        self.position = SignPosition.from_planet(ed.ut, planet, zodiac, signs, houses)
        self.dignity = self._get_planet_dignity(planet, signs)
        self.retrograde = self.position.speed < 0
        self._assign_scores()

    def _assign_scores(self) -> Tuple[float, float]:
        """Assign scores based on horo aspects"""
        self.score += ESSENTIAL_SCORE[self.dignity]
        if self.retrograde:
            self.score += RETROGRADE_SCORE

    def _get_decan(self, signs: BaseSplitter[Sign]) -> Optional[Planet]:
        """Get the ruling decan of the region"""
        sign = self.position.sign

        if sign not in DECANS:
            return None
        
        sign_limits = signs.get_ra_limits(sign, self.position.declination)
        face_length = sign_limits.length() / 3
        for face_index in range(3):
            face_start = face_index * face_length + sign_limits.a1.standard_value()
            face = AngleSegment(face_start, face_start + face_length)
            if face.check_collision(Angle(self.position.abs_angle), 0):
                return DECANS[sign][face_index]

        return None


    def _get_planet_dignity(self, planet: Planet, signs: BaseSplitter[Sign]) -> Dignity:
        """Get the dignity type of a planet"""
        sign = self.position.sign
        house = self.position.house
        opposite = signs.split(self.position.abs_angle + 180, -self.position.declination)
        triplicity = None
        if sign in ELEMENT_ASSOCIATION:
            triplicity = TRIPLICITIES[ELEMENT_ASSOCIATION[sign]][TRIPLICITY_TIME[house]]

        decan = self._get_decan(signs)            

        if RULERS[sign] == planet:
            return Dignity.DIGNITY
        if RULERS[opposite] == planet:
            return Dignity.DETRIMENT
        if planet in EXALTATIONS:
            if EXALTATIONS[planet][0] == sign:
                return Dignity.EXALTATION
            if EXALTATIONS[planet][0] == opposite:
                return Dignity.FALL
        if planet == decan:
            return Dignity.DECAN
        if planet == triplicity:
            return Dignity.TRIPLICITY
        return Dignity.NORMAL
    

class AspectHoroscope:
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
                return
            
        self.aspect = Aspect.NONE
        self.orb = 0


class Horoscope:
    """Complete horoscope summary"""

    planets: Dict[Planet, PlanetHoroscope]
    ascending: SignPosition
    midheaven: SignPosition
    main_signs: Dict[AngleSegment, Sign]
    extra_signs: Dict[AngleSegment, Sign]
    houses: Dict[AngleSegment, House]
    aspects: Dict[PlanetTuple, AspectHoroscope]

    house_splitter: HouseSplitter
    sign_splitter: SignSplitter

    date: EpheDate
    settings: EpheSettings

    def __init__(self, ed: EpheDate, settings: EpheSettings):
        self.date = ed
        self.settings = settings
        self.sign_splitter = SignSplitter(ed.obliquity, settings.zodiac)
        self.house_splitter = HouseSplitter(ed.ut, settings)

        self.planets = dict()
        extra_signs = []
        for planet in list(Planet):
            self.planets[planet] = PlanetHoroscope(
                ed,
                planet,
                settings.zodiac,
                self.sign_splitter,
                self.house_splitter
            )
            pos = self.planets[planet].position
            extra_signs.append((pos.sign, pos.abs_angle, pos.declination))

        self._get_all_aspects(settings)

        self.ascending, self.midheaven = self.house_splitter.get_ascmc(self.sign_splitter)
        self.houses = self.house_splitter.ring
        
        # Add main signs
        self.main_signs = dict()
        for sign in self.sign_splitter._split_deg(0).ring.values():
            seg = self.sign_splitter.get_ra_limits(sign, 0)
            self.main_signs[seg] = sign
        
        # Add extra signs
        self.extra_signs = dict()
        for sign, ra, dec in extra_signs:
            if sign == self.sign_splitter.split(ra, 0):
                continue
            seg = self.sign_splitter.get_ra_limits(sign, dec)
            self.extra_signs[seg] = sign
    
    def _get_all_aspects(self, settings: EpheSettings) -> Dict[PlanetTuple, AspectHoroscope]:
        self.aspects = dict()
        for p1, ph1 in self.planets.items():
            for p2, ph2 in self.planets.items():
                if p1.value >= p2.value:
                    continue
                aspect = AspectHoroscope(ph1, ph2, settings)
                if aspect.aspect != Aspect.NONE:
                    self.aspects[PlanetTuple(p1, p2)] = aspect
