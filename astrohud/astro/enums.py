from enum import Enum


class Sign(Enum):
    ARIES = 0
    TAURUS = 1
    GEMINI = 2
    CANCER = 3
    LEO = 4
    VIRGO = 5
    LIBRA = 6
    SCORPIO = 7
    SAGITTARIUS = 8
    CAPRICORN = 9
    AQUARIUS = 10
    PISCES = 11


class Planet(Enum):
    SUN = 0
    MOON = 1
    MERCURY = 2
    VENUS = 3
    MARS = 4
    JUPITER = 5
    SATURN = 6
    URANUS = 7
    NEPTUNE = 8
    PLUTO = 9
    PALLAS = 18
    ERIS = 146199


class House(Enum):
    IDENTITY_1 = 1
    MATERIAL_2 = 2
    INTELLECT_3 = 3
    ORIGINS_4 = 4
    PLEASURE_5 = 5
    HEALTH_6 = 6
    PARTNERS_7 = 7
    TRANSFORMATION_8 = 8
    SPIRITUALITY_9 = 9
    AMBITION_10 = 10
    COMMUNITY_11 = 11
    UNCONSCIOUS_12 = 12


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
    CONJUNCTION = 0
    SEXTILE = 1
    SQUARE = 2
    TRINE = 3
    OPPOSITION = 4

class Dignity(Enum):
    DETRIMENT = 0
    FALL = 1
    NORMAL = 2
    EXALTATION = 3
    DIGNITY = 4
