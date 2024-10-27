"""Base classes for models"""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Set

from PIL import ImageDraw
import numpy as np


class XY:
    """Class for chart coordinates."""

    array: np.ndarray

    def __init__(self, x: float = 0, y: float = 0, array: np.ndarray = None):
        self.array = np.array((x, y))
        if array:
            self.array = array

    @property
    def tuple(self):
        return tuple(self.array)
    
    @property
    def x(self):
        return self.array[0]
    
    @property
    def y(self):
        return self.array[1]


@dataclass(frozen=True)
class BaseCoord:
    """Base class for ecliptic coordinates."""

    ra: float  # Right ascension
    dec: float # Declination


class BaseChart(ABC):
    """Abstract class for a chart type."""

    draw: ImageDraw
    shapes: Set

    def __init__(self, draw: ImageDraw):
        """Constructor"""
        self.draw = draw
        self.shapes = set()

    @abstractmethod
    def convert_coord(coord: BaseCoord) -> XY:
        """Convert an ecliptic coordinate to chart XY."""


class BaseShape(ABC):
    """Abstract class for drawable shapes."""

    @abstractmethod
    def __hash__(self):
        """Should be hashable and immutable."""

    @abstractmethod
    def draw(self, chart: BaseChart):
        """Draw shape to chart"""
