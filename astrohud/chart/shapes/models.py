"""Common shape models"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from typing import Union
import os

from astrohud.chart._base.models import BaseCoord
from astrohud.chart._base.models import BaseShape


IMG_FOLDER =  os.path.join(os.path.dirname(__file__), '../../img')


@dataclass(frozen=True)
class Circle(BaseShape):
    center: BaseCoord
    edge: BaseCoord
    width: float = 8
    fill: bool = False


@dataclass(frozen=True)
class Line(BaseShape):
    a: BaseCoord
    b: BaseCoord
    width: float = 8


@dataclass(frozen=True)
class Arc(BaseShape):
    a: BaseCoord
    b: BaseCoord
    center: BaseCoord
    width: float = 8


@dataclass(frozen=True)
class Label(BaseShape):
    center: BaseCoord
    label: Union[str, Enum]
    small: bool = False

    def get_symbol_path(self, name: str) -> Optional[str]:
        """Get the path for a symbol, if it exists"""
        path = os.path.join(IMG_FOLDER, f'{name.lower()}.png')
        if not os.path.exists(path):
            return None
        return path

