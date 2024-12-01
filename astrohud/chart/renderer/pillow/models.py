"""Pillow renderer"""

from typing import Optional
from typing import Set
from typing import Tuple
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np

from astrohud.chart._base.const import COLOR_ALPHA
from astrohud.chart._base.const import COLOR_BLACK
from astrohud.chart._base.const import COLOR_WHITE
from astrohud.chart._base.models import BaseRenderer
from astrohud.chart._base.models import BaseShape
from astrohud.chart._base.models import XY
from astrohud.chart.shapes.const import IMG_SIZE_BIG
from astrohud.chart.shapes.const import IMG_SIZE_SMALL
from astrohud.chart.shapes.models import Arc
from astrohud.chart.shapes.models import Circle
from astrohud.chart.shapes.models import Label
from astrohud.chart.shapes.models import Line
from astrohud.lib.math.models import Angle


FONT_FILE = os.path.join(os.path.dirname(__file__), '../../../assets/font/HackNerdFont-Regular.ttf')
BIG_FONT = ImageFont.truetype(FONT_FILE, size=96, encoding='unic')
SMALL_FONT = ImageFont.truetype(FONT_FILE, size=48, encoding='unic')


class PillowRenderer(BaseRenderer):
    """Renderer using Pillow library"""
    img: Image
    draw: ImageDraw

    def __init__(self, chart):
        """Constructor"""
        super().__init__(chart)
        self.img = Image.new("RGBA", (chart.width, chart.width), COLOR_ALPHA)
        self.draw = ImageDraw.Draw(self.img)

    # Overrides

    def draw_shape(self, shape: BaseShape):
        """Draw a shape"""
        if isinstance(shape, Circle):
            self._draw_circle(shape)
        elif isinstance(shape, Line):
            self._draw_line(shape)
        elif isinstance(shape, Arc):
            self._draw_arc(shape)
        elif isinstance(shape, Label):
            self._draw_label(shape)

    def finish(self):
        """Finish drawing"""
        self._apply_outline()

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
    
    # Shape rendering
    
    def _draw_circle(self, shape: Circle):
        """Draw circle to chart"""
        center = self.chart.convert_coord(shape.center)
        edge = self.chart.convert_coord(shape.edge)
        radius = np.linalg.norm(center.array - edge.array)
        
        kwargs = dict()
        if shape.fill:
            kwargs.update(fill=COLOR_WHITE)

        self.draw.circle(center.tuple, radius, width=shape.width, outline=COLOR_WHITE, **kwargs)

    def _draw_line(self, shape: Line):
        """Draw line to chart"""
        a = self.chart.convert_coord(shape.a)
        b = self.chart.convert_coord(shape.b)
        self.draw.line(a.tuple + b.tuple, fill=COLOR_WHITE, width=shape.width)

    def _draw_arc(self, shape: Arc):
        """Draw arc to chart"""
        center = self.chart.convert_coord(shape.center)
        a = self.chart.convert_coord(shape.a).array - center.array
        b = self.chart.convert_coord(shape.b).array - center.array

        radius = np.linalg.norm(a)
        diagonal = np.sqrt(np.ones(2)) * radius + (shape.width / 2)
        box_min = XY(array=center.array - diagonal)
        box_max = XY(array=center.array + diagonal)

        phi1 = np.arctan2(a[1], a[0]) * 180 / np.pi
        phi2 = np.arctan2(b[1], b[0]) * 180 / np.pi

        a1, a2 = Angle.sort(Angle(phi1), Angle(phi2))

        self.draw.arc(box_min.tuple + box_max.tuple, a1.value, a2.value, fill=COLOR_WHITE, width=shape.width)

    def _draw_label(self, shape: Label):
        """Draw label to chart"""
        center = self.chart.convert_coord(shape.center)
        font = SMALL_FONT if shape.small else BIG_FONT
        size = IMG_SIZE_SMALL if shape.small else IMG_SIZE_BIG

        label = shape.label
        if isinstance(label, str):
            self.draw.text(center.tuple, label, font=font, fill=COLOR_WHITE, anchor='mm')
        else:
            path = shape.get_symbol_path(label.name)
            img = self._get_symbol(path, size)
            if img:
                start = XY(array=center.array - (img.width / 2))
                self.draw.bitmap(start.tuple, img, fill=COLOR_WHITE)

    # Pillow utilities

    def _get_symbol(self, path: str, size: int) -> Optional[Image.Image]:
        """Get a symbol"""
        if not path:
            return None
        img = Image.open(path)

        return img.convert('RGBA').resize((size, size))

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