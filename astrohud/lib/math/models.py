"""Models for math"""

from typing import Any
from typing import List


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
            error = f"'<' not supported between instances of 'Angle' and '{type(other).__name__}'"
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
