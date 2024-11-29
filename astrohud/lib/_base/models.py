"""Base classes for models."""

from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import Generic
from typing import Tuple
from typing import TypeVar


T = TypeVar('T')
class BaseSplitter(ABC,Generic[T]):
    """Split a spatial position into sections"""

    ring: Dict[float, T]

    def __init__(self):
        """Constructor"""
        self.ring = dict()

    def _split_deg(self, deg: float, round: bool = False) -> T:
        """Split a degree across self.ring"""
        best_option = None
        best_dist = 360
        for limit, option in self.ring.items():
            angle = (deg - limit) % 360
            if round:
                angle = abs(deg - limit) % 360
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

        splitter2d = self._split_deg(dec, round=True)
        return splitter2d.split(ra)
    
    def get_ra_limits(self, item: T, dec: float = 0) -> Tuple[float, float]:
        """Get the min and max ra for the item"""
        splitter = self._split_deg(dec, round=True)
        for min_angle, item2 in splitter.ring.items():
            if item != item2:
                continue
            return min_angle, splitter._split_next(min_angle)

        return None, None