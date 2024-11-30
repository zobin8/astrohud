"""Base classes for models."""

from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import Generic
from typing import Tuple
from typing import TypeVar

from astrohud.lib.math.models import Angle
from astrohud.lib.math.models import AngleSegment


T = TypeVar('T')
class BaseSplitter(ABC,Generic[T]):
    """Split a spatial position into sections"""

    ring: Dict[AngleSegment, T]
    default: T

    def __init__(self):
        """Constructor"""
        self.ring = dict()
        self.default = None

    def _split_deg(self, deg: float) -> T:
        """Split a degree across self.ring"""
        angle = Angle(deg)
        for segment, option in self.ring.items():
            if segment.check_collision(angle, limit=0):
                return option
        return self.default
    
    @abstractmethod
    def split(self, ra: float, dec: float = 0) -> T:
        """Split an ecliptic position"""
        pass
    

class Splitter2D(BaseSplitter[T]):
    """Split across right ascension"""

    def split(self, ra: float, dec: float = 0) -> T:
        """Split an ecliptic position"""
        item = self._split_deg(ra)
        return item
    

class Splitter3D(BaseSplitter[Splitter2D[T]]):
    """Split across right ascension and declination"""

    def split(self, ra: float, dec: float = 0) -> T:
        """Split an ecliptic position"""

        splitter2d = self._split_deg(dec)
        return splitter2d.split(ra)
    
    def get_ra_limits(self, item: T, dec: float = 0) -> AngleSegment:
        """Get the min and max ra for the item"""
        splitter = self._split_deg(dec)
        for segment, item2 in splitter.ring.items():
            if item != item2:
                continue
            return segment

        return None