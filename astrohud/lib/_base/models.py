"""Base classes for models."""

from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import Generic
from typing import Tuple
from typing import TypeVar

from astrohud.lib.math.models import Angle


T = TypeVar('T')
class BaseSplitter(ABC,Generic[T]):
    """Split a spatial position into sections"""

    ring: Dict[float, T]

    def __init__(self):
        """Constructor"""
        self.ring = dict()

    def _split_deg(self, deg: float, round: bool = False, invert: bool = False) -> Tuple[float, T]:
        """Split a degree across self.ring"""
        best_deg = None
        best_option = None
        best_dist = 360
        for limit, option in self.ring.items():
            diff = Angle(deg).compare(Angle(limit))
            if invert:
                diff *= -1
            if round:
                diff = abs(diff)
            if diff < best_dist and diff >= 0:
                best_dist = diff
                best_deg = limit
                best_option = option
        return best_deg, best_option
    
    def _split_next(self, deg: float) -> float:
        """Get the next degree across self.ring"""
        best_option = None
        best_dist = 360
        for limit in self.ring.keys():
            if limit == deg:
                continue
            diff = -Angle(deg).compare(Angle(limit))
            if diff < best_dist and diff >= 0:
                best_dist = diff
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
        _, item = self._split_deg(ra)
        return item
    

class Splitter3D(BaseSplitter[Splitter2D[T]]):
    """Split across right ascension and declination"""

    def split(self, ra: float, dec: float = 0) -> T:
        """Split an ecliptic position"""

        _, splitter2d = self._split_deg(dec, round=True)
        return splitter2d.split(ra)
    
    def get_ra_limits(self, item: T, dec: float = 0) -> Tuple[float, float]:
        """Get the min and max ra for the item"""
        _, splitter = self._split_deg(dec, round=True)
        for min_angle, item2 in splitter.ring.items():
            if item != item2:
                continue
            max_angle, _ = splitter._split_deg(min_angle + 1, invert=True)
            return min_angle, max_angle

        return None, None