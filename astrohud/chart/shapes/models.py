"""Common shape models"""

from dataclasses import dataclass
from typing import Union
from enum import Enum
import os

import numpy as np
from PIL import Image
from PIL import ImageFont

from astrohud.chart._base.const import COLOR_ALPHA
from astrohud.chart._base.const import COLOR_BLACK
from astrohud.chart._base.const import COLOR_WHITE
from astrohud.chart._base.models import BaseChart
from astrohud.chart._base.models import BaseCoord
from astrohud.chart._base.models import BaseShape
from astrohud.chart._base.models import XY



FONT_FILE = os.path.join(os.path.dirname(__file__), '../../font/HackNerdFont-Regular.ttf')
IMG_FOLDER =  os.path.join(os.path.dirname(__file__), '../../img')
BIG_FONT = ImageFont.truetype(FONT_FILE, size=96, encoding='unic')
SMALL_FONT = ImageFont.truetype(FONT_FILE, size=48, encoding='unic')


@dataclass(frozen=True)
class Circle(BaseShape):
    center: BaseCoord
    edge: BaseCoord
    width: float = 8
    fill: bool = False

    def draw(self, chart: BaseChart):
        """Draw shape to chart"""
        center = chart.convert_coord(self.center)
        edge = chart.convert_coord(self.edge)
        radius = np.linalg.norm(center.array - edge.array)
        
        kwargs = dict()
        if self.fill:
            kwargs.update(fill=COLOR_WHITE)

        chart.draw.circle(center.tuple, radius, width=self.width, outline=COLOR_WHITE, **kwargs)


@dataclass(frozen=True)
class Line(BaseShape):
    a: BaseCoord
    b: BaseCoord
    width: float = 8

    def draw(self, chart: BaseChart):
        """Draw shape to chart"""
        a = chart.convert_coord(self.a)
        b = chart.convert_coord(self.b)
        chart.draw.line(a.tuple + b.tuple, fill=COLOR_WHITE, width=self.width)


@dataclass(frozen=True)
class Arc(BaseShape):
    a: BaseCoord
    b: BaseCoord
    center: BaseCoord
    width: float = 8

    def draw(self, chart: BaseChart):
        """Draw shape to chart"""
        center = chart.convert_coord(self.center)
        a = chart.convert_coord(self.a).array - center.array
        b = chart.convert_coord(self.b).array - center.array

        radius = np.linalg.norm(a)
        diagonal = np.sqrt(np.ones(2)) * radius + (self.width / 2)
        box_min = XY(array=center.array - diagonal)
        box_max = XY(array=center.array + diagonal)

        phi1 = np.arctan2(a[1], a[0]) * 180 / np.pi
        phi2 = np.arctan2(b[1], b[0]) * 180 / np.pi

        # ZTODO angle math
        while phi1 - 180 > phi2:
            phi2 += 360
        while phi1 + 180 < phi2:
            phi2 -= 360

        if phi1 > phi2:
            phi1, phi2 = phi2, phi1

        chart.draw.arc(box_min.tuple + box_max.tuple, phi1, phi2, fill=COLOR_WHITE, width=self.width)


@dataclass(frozen=True)
class Label(BaseShape):
    center: BaseCoord
    label: Union[str, Enum]
    small: bool = False

    def _get_symbol(self, name: str) -> Image.Image:
        img = Image.open(os.path.join(IMG_FOLDER, f'{name.lower()}.png'))

        return img.convert('RGBA').resize((150, 150))
    
    def draw(self, chart: BaseChart):
        """Draw shape to chart"""
        center = chart.convert_coord(self.center)
        font = SMALL_FONT if self.small else BIG_FONT
        if isinstance(self.label, str):
            chart.draw.text(center.tuple, self.label, font=font, fill=COLOR_WHITE, anchor='mm')
        else:
            img = self._get_symbol(self.label.name)
            start = XY(array=center.array - (img.width / 2))
            chart.draw.bitmap(start.tuple, img, fill=COLOR_WHITE)
