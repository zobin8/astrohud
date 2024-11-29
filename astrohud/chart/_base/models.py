"""Base classes for models"""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Set

from PIL import Image
from PIL import ImageDraw
import numpy as np

from .const import COLOR_ALPHA
from .const import IMAGE_PAD
from .const import MAX_RADIUS


class XY:
    """Class for chart coordinates."""

    array: np.ndarray

    def __init__(self, x: float = 0, y: float = 0, array: np.ndarray = None):
        self.array = np.array((x, y))
        if array is not None:
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

    ra: float = 0   # Right ascension
    dec: float = 0  # Declination


class BaseChart(ABC):
    """Abstract class for a chart type."""
    shapes: Set
    width: float

    def __init__(self):
        """Constructor"""
        self.shapes = set()
        self.width = (MAX_RADIUS + IMAGE_PAD) * 2 + 1

    @abstractmethod
    def convert_coord(coord: BaseCoord) -> XY:
        """Convert an ecliptic coordinate to chart XY."""


class BaseShape(ABC):
    """Abstract class for drawable shapes."""

    @abstractmethod
    def __hash__(self):
        """Should be hashable and immutable."""


class BaseRenderer(ABC):
    """Abstract class for shape renderer."""

    chart: BaseChart

    def __init__(self, chart: BaseChart):
        """Constructor"""
        self.chart = chart

    def draw_all(self):
        """Draw the whole chart"""
        for shape in self.chart.shapes:
            self.draw_shape(shape)
        self.finish()

    @abstractmethod
    def draw_shape(self, shape: BaseShape):
        """Draw a shape"""

    @abstractmethod
    def finish(self):
        """Finish drawing"""
