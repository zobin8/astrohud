"""Enums for horoscopes"""

from enum import Enum


class Element(Enum):
    FIRE = 0
    AIR = 1
    Earth = 2
    Water = 3


class Polarity(Enum):
    NEGATIVE = 0
    POSITIVE = 1


class Modality(Enum):
    CARDINAL = 0
    FIXED = 1
    MUTABLE = 2


class Aspect(Enum):
    NONE = -1
    CONJUNCTION = 0
    SEXTILE = 1
    SQUARE = 2
    TRINE = 3
    OPPOSITION = 4


class Dignity(Enum):
    DETRIMENT = 0
    FALL = 1
    NORMAL = 2
    TRIPLICITY = 3
    EXALTATION = 4
    DIGNITY = 5
