"""Constants for ephemeris"""

from .enums import HouseSystem
from .enums import Zodiac
from .enums import Planet


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
    Zodiac.IAU.name: '13 signs, based on the IAU divisions of the ecliptic',
    Zodiac.STELLAR.name: 'All 88 IAU signs, using the 3D position of the stars',
}


PLANET_DESCRIPTIONS = {
    Planet.SUN.name: 'Classical planet, star',
    Planet.MOON.name: 'Classical planet, moon',
    Planet.MERCURY.name: 'Classical planet, inner planet',
    Planet.VENUS.name: 'Classical planet, inner planet',
    Planet.MARS.name: 'Classical planet, inner planet',
    Planet.JUPITER.name: 'Classical planet, outer planet',
    Planet.SATURN.name: 'Classical planet, outer planet',
    Planet.URANUS.name: 'Outer planet',
    Planet.NEPTUNE.name: 'Outer planet',
    Planet.PLUTO.name: 'Minor planet, dwarf planet',
    Planet.PALLAS.name: 'Minor planet, asteroid',
    Planet.ERIS.name: 'Minor planet, dwarf planet',
}
