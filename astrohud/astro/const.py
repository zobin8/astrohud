from .enums import Aspect
from .enums import Planet
from .enums import Sign
from .enums import Polarity
from .enums import Modality
from .enums import Element


RULERS = {
    Sign.ARIES: Planet.MARS,
    Sign.TAURUS: Planet.VENUS,
    Sign.GEMINI: Planet.MERCURY,
    Sign.CANCER: Planet.MOON,
    Sign.LEO: Planet.SUN,
    Sign.VIRGO: Planet.CERES,
    Sign.LIBRA: Planet.PALLAS,
    Sign.SCORPIO: Planet.PLUTO,
    Sign.SAGITTARIUS: Planet.JUPITER,
    Sign.CAPRICORN: Planet.SATURN,
    Sign.AQUARIUS: Planet.URANUS,
    Sign.PISCES: Planet.NEPTUNE,
}


EXALTATIONS = {
    Planet.SUN: (Sign.ARIES, 19),
    Planet.MOON: (Sign.TAURUS, 3),
    Planet.MERCURY: (Sign.VIRGO, 15),
    Planet.VENUS: (Sign.PISCES, 24),
    Planet.MARS: (Sign.CAPRICORN, 28),
    Planet.JUPITER: (Sign.CANCER, 15),
    Planet.SATURN: (Sign.LIBRA, 21),
}


POLARITY_ASSOCIATION = {
    Element.FIRE: Polarity.POSITIVE,
    Element.AIR: Polarity.POSITIVE,
    Element.Water: Polarity.NEGATIVE,
    Element.Earth: Polarity.NEGATIVE,
}


ELEMENT_ASSOCIATION = {
    Sign.ARIES: Element.FIRE,
    Sign.TAURUS: Element.Earth,
    Sign.GEMINI: Element.AIR,
    Sign.CANCER: Element.Water,
    Sign.LEO: Element.FIRE,
    Sign.VIRGO: Element.Earth,
    Sign.LIBRA: Element.AIR,
    Sign.SCORPIO: Element.Water,
    Sign.SAGITTARIUS: Element.FIRE,
    Sign.CAPRICORN: Element.Earth,
    Sign.AQUARIUS: Element.AIR,
    Sign.PISCES: Element.Water,
}


MODALITY_ASSOCIATIONS = {
    Sign.ARIES: Modality.CARDINAL,
    Sign.TAURUS: Modality.FIXED,
    Sign.GEMINI: Modality.MUTABLE,
    Sign.CANCER: Modality.CARDINAL,
    Sign.LEO: Modality.FIXED,
    Sign.VIRGO: Modality.MUTABLE,
    Sign.LIBRA: Modality.CARDINAL,
    Sign.SCORPIO: Modality.FIXED,
    Sign.SAGITTARIUS: Modality.MUTABLE,
    Sign.CAPRICORN: Modality.CARDINAL,
    Sign.AQUARIUS: Modality.FIXED,
    Sign.PISCES: Modality.MUTABLE,
}


ASPECT_DEGREES = {
    Aspect.CONJUNCTION: 0,
    Aspect.SEXTILE: 60,
    Aspect.SQUARE: 90,
    Aspect.TRINE: 120,
    Aspect.OPPOSITION: 180,
}