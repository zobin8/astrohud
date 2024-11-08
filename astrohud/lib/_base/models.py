"""Base classes for models."""

from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Any
from typing import Dict
from typing import Generic
from typing import Tuple
from typing import TypeVar


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


T = TypeVar('T')
class BaseSplitter(ABC,Generic[T]):
    """Split a spatial position into sections"""

    ring: Dict[float, T]

    def __init__(self):
        """Constructor"""
        self.ring = dict()

    def _split_deg(self, deg: float) -> T:
        """Split a degree across self.ring"""
        best_option = None
        best_dist = 360
        for limit, option in self.ring.items():
            angle = (deg - limit) % 360
            if angle < best_dist:
                best_dist = angle
                best_option = option
        return best_option
    
    def _split_next(self, deg: float) -> float:
        """Get the next degree across self.ring"""
        best_option = None
        best_dist = 360
        for limit in self.ring.keys():
            if limit == deg:
                continue
            angle = (limit - deg) % 360
            if angle < best_dist:
                best_dist = angle
                best_option = limit
        return best_option
    
    @abstractmethod
    def split(self, ra: float, dec: float = 0) -> T:
        """Split an ecliptic position"""
        pass
    

class Splitter2D(BaseSplitter[T]):
    """Split across right ascension"""

    def split(self, ra: float, dec: float = 0) -> T:
        """Split an ecliptic position"""
        return self._split_deg(ra)
    

class Splitter3D(BaseSplitter[Splitter2D[T]]):
    """Split across right ascension and declination"""

    def split(self, ra: float, dec: float = 0) -> T:
        """Split an ecliptic position"""

        splitter2d = self._split_deg(dec)
        return splitter2d.split(ra)
    
    def get_ra_limits(self, item: T, dec: float = 0) -> Tuple[float, float]:
        """Get the min and max ra for the item"""
        splitter = self._split_deg(dec)
        for min_angle, item2 in splitter.ring.items():
            if item != item2:
                continue
            return min_angle, splitter._split_next(min_angle)

        return None, None