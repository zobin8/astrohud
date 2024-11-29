"""Models for math"""

from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple


class Angle:
    """Math utility for an angle, in degrees"""

    value: float
    center: float

    def __init__(self, value: float, center: float = 0):
        """Constructor"""
        offset = center - 180
        self.value = ((value - offset) % 360) + offset
        self.center = center

    def standard_value(self) -> float:
        """Get unique standardized value"""
        return Angle(self.value).value
    
    def positive_value(self) -> float:
        """Get unique positive value"""
        return Angle(self.value, 180).value

    # Comparison methods

    def __eq__(self, other: Any) -> bool:
        """Check value equality"""
        if not isinstance(other, Angle):
            return False
        
        return self.standard_value() == other.standard_value()
    
    def compare(self, other: Any) -> float:
        """Compare against another angle, and return a float.
        
        A positive return value implies other is greater.
        """
        if not isinstance(other, Angle):
            error = f"Operation not supported between instances of 'Angle' and '{type(other).__name__}'"
            raise TypeError(error)
        
        diff = Angle(self.value, other.value)
        return diff.value - diff.center
    
    def __lt__(self, other: Any):
        """Check value less than, around a common center"""
        
        return self.compare(other) < 0

    def __le__(self, other: Any):
        """Check value less than or equal, around a common center"""
        
        return self.compare(other) <= 0

    # Conversion methods

    def __hash__(self) -> int:
        """Get hash code"""
        return hash(self.standard_value())
    
    def __repr__(self) -> str:
        """Get string representation"""
        return f'Angle({self.value}, {self.center})'
    
    # Math methods

    def average(self, other: Any) -> Any:
        """Get the average of two angles."""
        comp = self.compare(other)
        comp /= 2
        return Angle(other.standard_value() + comp)
    
    def distance(self, other: Any) -> float:
        """Get the distance between two angles."""
        return abs(self.compare(other))

    @classmethod
    def sort(cls, a1: Any, a2: Any) -> Tuple[Any, Any]:
        """Sort two angles"""
        if a2 < a1:
            a1, a2 = a2, a1

        out1 = Angle(a1.value, a1.value)
        out2 = Angle(a2.value, a1.value)

        return out1, out2


class AngleSegment:
    """Math utility for a segment between two angles."""

    a1: Angle
    a2: Angle

    def __init__(self, a1: float|Angle, a2: float|Angle):
        """Constructor"""
        if isinstance(a1, float):
            a1 = Angle(a1)
        if isinstance(a2, float):
            a2 = Angle(a2)

        self.a1, self.a2 = Angle.sort(a1, a2)

    # Comparison methods
    def __eq__(self, other: Any):
        """Compare equality to another AngleSegment"""
        if not isinstance(other, AngleSegment):
            error = f"Operation not supported between instances of 'AngleSegment' and '{type(other).__name__}'"
            raise TypeError(error)
        return self.a1 == other.a1 and self.a2 == other.a2

    # Conversion methods

    def __hash__(self) -> int:
        """Get hash code"""
        return hash((self.a1, self.a2))
    
    def __repr__(self) -> str:
        """Get string representation"""
        return f'AngleSegment({self.a1.value}, {self.a2.value})'
    
    def __iter__(self) -> Iterator[Angle]:
        """Iterate over the angles"""
        return iter((self.a1, self.a2))

    # Math methods

    def check_collision(self, other: Any, limit: float) -> bool:
        """Check if it collides with another AngleSegment, within a given limit"""
        if isinstance(other, Angle):
            other = AngleSegment(other, other)

        comp_start = self.a2.compare(other.a2)
        if comp_start < 0:
            cross = self.a2.compare(other.a1) + limit
        else:
            cross = other.a2.compare(self.a1) + limit
        return cross > 0
    
    def length(self) -> float:
        """Get the segment length"""
        return self.a1.distance(self.a2)
    
    def middle(self) -> Angle:
        """Get the middle angle"""
        return self.a1.average(self.a2)


class UnionFind:
    """Simple union-find datastructure"""
    parents: Dict[Any, Any]
    members: Dict[Any, set]

    def __init__(self) -> None:
        """Constructor"""
        self.parents = dict()
        self.members = dict()

    def add(self, item: Any):
        """Add an item to the structure"""
        if item not in self.parents:
            self.parents[item] = item
            self.members[item] = {item}

    def find(self, item: Any) -> Any:
        """Find an item's root"""
        parent = self.parents.get(item, None)
        if parent is None or parent == item:
            return parent
        self.parents[item] = self.find(parent)
        return self.parents[item]
    
    def union(self, item1: Any, item2: Any):
        """Connect two items in the structure"""
        self.add(item1)
        self.add(item2)
        item1 = self.find(item1)
        item2 = self.find(item2)

        if item1 == item2:
            return
        
        if len(self.members[item1]) < len(self.members[item2]):
            item1, item2 = item2, item1

        self.parents[item2] = item1
        self.members[item1] = self.members[item1].union(self.members.pop(item2))