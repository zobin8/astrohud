from typing import List
from dataclasses import dataclass


@dataclass
class RenderSettings:
    """Settings for drawing the horoscope"""

    asc_angle: float
    cusps: List[float]
