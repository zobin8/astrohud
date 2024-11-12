"""Base classes for models"""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Set
from typing import Tuple

from PIL import Image
from PIL import ImageDraw
import numpy as np

from .const import COLOR_ALPHA
from .const import COLOR_BLACK
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

    img: Image
    draw: ImageDraw
    shapes: Set

    def __init__(self):
        """Constructor"""
        self.shapes = set()
        width = (MAX_RADIUS + IMAGE_PAD) * 2 + 1
        self.img = Image.new("RGBA", (width, width), COLOR_ALPHA)
        self.draw = ImageDraw.Draw(self.img)

    @abstractmethod
    def convert_coord(coord: BaseCoord) -> XY:
        """Convert an ecliptic coordinate to chart XY."""

    def overlay_image(self, background: str, shift: float = 0) -> Image.Image:
        """Overlay the chart on the given background image"""
        img = Image.open(background)
        size = min(img.height, img.width)
        overlay = self.img.resize((size, size))
        x = (img.width - size) // 2
        y = (img.height - size) // 2

        x += int(x * shift)
        y += int(y * shift)

        img.alpha_composite(overlay, (x, y))
        return img
    
    def finish(self):
        """Draw chart"""
        for shape in self.shapes:
            shape.draw(self)

        self._apply_outline()

    def _get_pixels(self) -> Set[Tuple[int, int]]:
        """Get all non-alpha pixel locations"""
        pixels = set()
        for i, pix in enumerate(self.img.getdata()):
            if pix != COLOR_ALPHA:
                xy = i % self.img.width, i // self.img.width
                pixels.add(xy)
        return pixels

    def _apply_outline(self) -> Image.Image:
        """Apply a black outline to any set pixels"""
        pixels = {xy: 0 for xy in self._get_pixels()}
        
        fringe = set(pixels.keys())
        while len(fringe) > 0:
            x, y = fringe.pop()
            level = pixels[(x, y)] + 1
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                xy2 = x + offset[0], y + offset[1]
                if pixels.get(xy2, 100) <= level or level > 5 or \
                    xy2[0] < 0 or xy2[1] < 0 or \
                    xy2[0] >= self.img.width or xy2[1] >= self.img.height:
                    continue
                pixels[xy2] = level
                fringe.add(xy2)
                self.img.putpixel(xy2, COLOR_BLACK)


class BaseShape(ABC):
    """Abstract class for drawable shapes."""

    @abstractmethod
    def __hash__(self):
        """Should be hashable and immutable."""

    @abstractmethod
    def draw(self, chart: BaseChart):
        """Draw shape to chart"""
