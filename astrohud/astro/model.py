from dataclasses import dataclass
from abc import ABC
from typing import Any
from typing import Dict
from typing import Tuple
from enum import Enum

from astrohud.astro.enums import Aspect
from astrohud.astro.enums import Dignity
from astrohud.astro.enums import House
from astrohud.astro.enums import Planet
from astrohud.astro.enums import Sign


class BaseMatchable(ABC):
    """A class that a JSON filter can match against"""

    @staticmethod
    def _obj_to_json(obj: Any) -> Any:
        """Turn an object into a matchable json type"""

        if isinstance(obj, BaseMatchable):
            return obj.to_json()
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, dict):
            return {
                BaseMatchable._obj_to_json(k): BaseMatchable._obj_to_json(v)
                for k, v in obj.items()
                }
        if isinstance(obj, str):
            return obj.upper()
        return obj
    
    @staticmethod
    def _match(obj: Any, filter: Any) -> bool:
        """Match object against json filter"""
        obj_json = BaseMatchable._obj_to_json(obj)
        filter_json = BaseMatchable._obj_to_json(filter)

        if type(filter_json) != type(obj_json):
            raise Exception(f'Invalid filter, type mismatch: obj {obj_json} and filter {filter_json}')
        
        if not isinstance(filter_json, dict):
            return filter_json == obj_json
        
        for key in filter_json.keys():
            if key not in obj_json:
                return False
            
            if not BaseMatchable._match(obj_json[key], filter_json[key]):
                return False

        return True
    
    def match(self, filter: Dict[str, Any]) -> bool:
        """Match against json filter"""
        return self._match(self, filter)
    
    def to_json(self):
        """Turn self into a matchable json type. Can be overridden."""
        out = dict()
        for key in self.__dataclass_fields__:
            value = getattr(self, key)
            out[BaseMatchable._obj_to_json(key)] = BaseMatchable._obj_to_json(value)
        return out


@dataclass
class SignPosition(BaseMatchable):
    """The position within a single sign"""

    abs_angle: float    # degrees from start
    sign: Sign          # Sign
    sign_angle: float   # degrees from sign
    speed: float        # degrees / day
    house: House        # House


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


@dataclass
class AspectHoroscope(BaseMatchable):
    """The horoscope for a single aspect"""

    aspect: Aspect
    orb: float


@dataclass
class PlanetHoroscope(BaseMatchable):
    """Horoscope summary for a single planet"""

    position: SignPosition
    dignity: Dignity
    retrograde: bool


@dataclass
class Horoscope(BaseMatchable):
    """Complete horoscope summary"""

    planets: Dict[Planet, PlanetHoroscope]
    ascending: SignPosition
    cusps: Dict[House, float]
    aspects: Dict[PlanetTuple, AspectHoroscope]


@dataclass
class HoroscopeSettings:
    """Settings for rendering horoscopes"""

    orb_limit: float
    location: Tuple[float, float]
    sidereal: bool
    aspects: bool
