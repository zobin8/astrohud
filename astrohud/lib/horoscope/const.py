"""Constants for horoscopes"""

from collections import defaultdict

from astrohud.lib.ephemeris.enums import Planet
from astrohud.lib.ephemeris.enums import Sign
from astrohud.lib.ephemeris.enums import House

from .enums import Aspect
from .enums import Dignity
from .enums import Element
from .enums import Modality
from .enums import Polarity


RULERS = defaultdict(lambda: None)
RULERS.update({
    Sign.ARIES: Planet.MARS,
    Sign.TAURUS: Planet.VENUS,
    Sign.GEMINI: Planet.MERCURY,
    Sign.CANCER: Planet.MOON,
    Sign.LEO: Planet.SUN,
    Sign.VIRGO: Planet.ERIS,
    Sign.LIBRA: Planet.PALLAS,
    Sign.SCORPIO: Planet.PLUTO,
    Sign.SAGITTARIUS: Planet.JUPITER,
    Sign.CAPRICORN: Planet.SATURN,
    Sign.AQUARIUS: Planet.URANUS,
    Sign.PISCES: Planet.NEPTUNE,
    Sign.OPHIUCHUS: Planet.PLUTO,
})


EXALTATIONS = {
    Planet.SUN: (Sign.ARIES, 19),
    Planet.MOON: (Sign.TAURUS, 3),
    Planet.MERCURY: (Sign.VIRGO, 15),
    Planet.VENUS: (Sign.PISCES, 24),
    Planet.MARS: (Sign.CAPRICORN, 28),
    Planet.JUPITER: (Sign.CANCER, 15),
    Planet.SATURN: (Sign.LIBRA, 21),
}


TRIPLICITY_TIME = {
    House.IDENTITY_1: 2,
    House.MATERIAL_2: 1,
    House.INTELLECT_3: 1,
    House.ORIGINS_4: 1,
    House.PLEASURE_5: 1,
    House.HEALTH_6: 2,
    House.PARTNERS_7: 2,
    House.TRANSFORMATION_8: 0,
    House.SPIRITUALITY_9: 0,
    House.AMBITION_10: 0,
    House.COMMUNITY_11: 0,
    House.UNCONSCIOUS_12: 2,
}


TRIPLICITIES = {
    Element.FIRE: (Planet.SUN, Planet.JUPITER, Planet.SATURN),
    Element.Earth: (Planet.VENUS, Planet.MOON, Planet.MARS),
    Element.AIR: (Planet.PALLAS, Planet.MERCURY, Planet.PLUTO),
    Element.Water: (Planet.URANUS, Planet.NEPTUNE, Planet.ERIS),
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
    Sign.OPHIUCHUS: Element.Water,
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
    Sign.OPHIUCHUS: Modality.FIXED,
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


ESSENTIAL_SCORE = defaultdict(list)
ESSENTIAL_SCORE.update({
    Aspect.CONJUNCTION: [5],
    Aspect.TRINE: [3],
    Aspect.SEXTILE: [2],
    Aspect.OPPOSITION: [4, -4],
    Aspect.SQUARE: [-3],

    Dignity.DETRIMENT: [-5],
    Dignity.FALL: [-4],
    Dignity.TRIPLICITY: [3],
    Dignity.EXALTATION: [4],
    Dignity.DIGNITY: [5],
})
