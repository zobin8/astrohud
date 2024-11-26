"""Enums for Wheel chart"""

from enum import Enum


class Collision(Enum):
    NONE = 0x0  # No collision
    OUTER = 0x1  # Collision, sign should go outside
    INNER = 0x2  # Collision, sign should go inside