"""Constants for ephemeris"""

from .enums import HouseSystem
from .enums import Zodiac


HOUSE_SYS_DESCRIPTIONS = {
    HouseSystem.PLACIDUS.name: 'Divide houses proportional to time spent travelling across the sky. Popular in western astrology.',
    HouseSystem.KOCH.name: 'Divide houses based on the horizon at different times.',
    HouseSystem.PORPHYRIUS.name: 'Every quadrant is equally divided into three',
    HouseSystem.REGIOMONTANUS.name: 'Space-oriented system invented by Regiomontanus',
    HouseSystem.CAMPANUS.name: 'Space-oriented system by Campanus',
    HouseSystem.EQUAL_ASCENDANT.name: '12 equal segments, starting with the ascendant',
    HouseSystem.EQUAL_ARIES.name: '12 equal segments, starting with Aries',
    HouseSystem.WHOLE_SIGNS.name: 'Each sign is a house, starting with Aries',
}

ZODIAC_DESCRIPTIONS = {
    Zodiac.TROPICAL.name: '12 equal segments starting at the equinox',
    Zodiac.SIDEREAL.name: '12 equal segments corrected using fixed stars',
    Zodiac.IAU.name: '13 signs matching the star\'s 2D position on the ecliptic',
    Zodiac.PLANETARIUM.name: '87 signs, using the 3D position of the stars',
}
