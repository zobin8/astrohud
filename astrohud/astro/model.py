from dataclasses import dataclass
from typing import Dict

from astrohud.astro.enums import Aspect
from astrohud.astro.enums import House
from astrohud.astro.enums import Planet
from astrohud.astro.enums import Sign


@dataclass
class SignPosition:
    abs_angle: float    # degrees from start
    sign: Sign          # Sign
    sign_angle: float   # degrees from sign
    speed: float        # degrees / day
    house: House        # House


@dataclass(frozen=True)
class PlanetTuple:
    planet1: Planet
    planet2: Planet

    def __post_init__(self):
        if self.planet2.value < self.planet1.value:
            self.planet1, self.planet2 = self.planet2, self.planet1


@dataclass
class AspectHoroscope:
    aspect: Aspect
    orb: float


@dataclass
class PlanetHoroscope:
    position: SignPosition


@dataclass
class Horoscope:
    planets: Dict[Planet, PlanetHoroscope]
    ascending: Sign
    aspects: Dict[PlanetTuple, AspectHoroscope]