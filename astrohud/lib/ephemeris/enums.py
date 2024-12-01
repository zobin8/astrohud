"""Enums for ephemeris"""

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
    OPHIUCHUS = 12
    ANDROMEDA = 13
    ANTLIA = 14
    APUS = 15
    AQUILA = 16
    ARA = 17
    AURIGA = 18
    BOOTES = 19
    CAELUM = 20
    CAMELOPARDALIS = 21
    CANES_VENATICI = 22
    CANIS_MAJOR = 23
    CANIS_MINOR = 24
    CARINA = 25
    CASSIOPEIA = 26
    CENTAURUS = 27
    CEPHEUS = 28
    CETUS = 29
    CHAMAELEON = 30
    CIRCINUS = 31
    COLUMBA = 32
    COMA_BERENICES = 33
    CORONA_AUSTRALIS = 34
    CORONA_BOREALIS = 35
    CORVUS = 36
    CRATER = 37
    CRUX = 38
    CYGNUS = 39
    DELPHINUS = 40
    DORADO = 41
    DRACO = 42
    EQUULEUS = 43
    ERIDANUS = 44
    FORNAX = 45
    GRUS = 46
    HERCULES = 47
    HOROLOGIUM = 48
    HYDRA = 49
    HYDRUS = 50
    INDUS = 51
    LACERTA = 52
    LEO_MINOR = 53
    LEPUS = 54
    LUPUS = 55
    LYNX = 56
    LYRA = 57
    MENSA = 58
    MICROSCOPIUM = 59
    MONOCEROS = 60
    MUSCA = 61
    NORMA = 62
    OCTANS = 63
    ORION = 64
    PAVO = 65
    PEGASUS = 66
    PERSEUS = 67
    PHOENIX = 68
    PICTOR = 69
    PISCIS_AUSTRINUS = 70
    PUPPIS = 71
    PYXIS = 72
    RETICULUM = 73
    SAGITTA = 74
    SCULPTOR = 75
    SCUTUM = 76
    SERPENS_CAPUT = 77
    SERPENS_CAUDA = 78
    SEXTANS = 79
    TELESCOPIUM = 80
    TRIANGULUM_AUSTRALE = 81
    TRIANGULUM = 82
    TUCANA = 83
    URSA_MAJOR = 84
    URSA_MINOR = 85
    VELA = 86
    VOLANS = 87
    VULPECULA = 88


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


class HouseSystem(Enum):
    PLACIDUS = 'P'
    KOCH = 'K'
    PORPHYRIUS = 'O'
    REGIOMONTANUS = 'R'
    CAMPANUS = 'C'
    EQUAL_ASCENDANT = 'A'
    WHOLE_SIGNS = 'W'
    EQUAL_ARIES = 'N'


class Zodiac(Enum):
    TROPICAL = 0
    SIDEREAL = 1
    IAU = 2
    STELLAR = 3
