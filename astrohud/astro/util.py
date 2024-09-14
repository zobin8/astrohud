from datetime import datetime
from datetime import timezone
from typing import Dict
from typing import Optional
from typing import Tuple
import os

import swisseph as swe

from astrohud.astro.const import ASPECT_DEGREES
from astrohud.astro.const import RULERS
from astrohud.astro.const import EXALTATIONS
from astrohud.astro.enums import Dignity
from astrohud.astro.enums import House
from astrohud.astro.enums import Planet
from astrohud.astro.enums import Sign
from astrohud.astro.model import AspectHoroscope
from astrohud.astro.model import Horoscope
from astrohud.astro.model import PlanetHoroscope
from astrohud.astro.model import PlanetTuple
from astrohud.astro.model import SignPosition


def init_ephe():
    dirname = os.path.dirname(__file__)
    ephe_path = os.path.join(dirname, '../../submodules/swisseph/ephe')
    swe.set_ephe_path(ephe_path)


def date_to_ut(date: datetime) -> float:
    assert date.tzinfo == timezone.utc
    date_tup = date.timetuple()[:6]
    et, ut = swe.utc_to_jd(*date_tup, swe.GREG_CAL)
    return ut


def get_sign(position: float) -> Tuple[Sign, float]:
    deg, min, sec, secfr, sign = swe.split_deg(position, 8)
    sec += secfr
    min += sec / 60
    deg += min / 60

    return Sign(sign), deg


def get_planet_pos(ut: float, planet: Planet, ascendant: Sign) -> SignPosition:
    results, flags = swe.calc_ut(ut, planet.value, flags=swe.FLG_SPEED)
    position=results[0]
    speed=results[3]

    sign, deg = get_sign(position)
    house = (sign.value - ascendant.value) % len(House) + 1

    return SignPosition(
        abs_angle=position,
        sign=sign,
        sign_angle=deg,
        speed=speed,
        house=House(house),
    )


def get_ascendant(ut: float, lat: float, lon: float) -> Sign:
    _, angles = swe.houses(ut, lat, lon, hsys=b'W')
    ascendant = angles[0]
    return get_sign(ascendant)[0]


def get_aspect(p1: PlanetHoroscope, p2: PlanetHoroscope, orb_limit=float) -> Optional[AspectHoroscope]:
    angle = abs(p1.position.abs_angle - p2.position.abs_angle)
    if angle > 180:
        angle = 360 - angle

    for aspect, target_angle in ASPECT_DEGREES.items():
        orb = abs(angle - target_angle)
        if orb < orb_limit:
            return AspectHoroscope(
                aspect=aspect,
                orb=orb,
            )
        
    return None


def get_all_aspects(planets: Dict[Planet, PlanetHoroscope], orb_limit: float) -> Dict[PlanetTuple, AspectHoroscope]:
    out = dict()
    for p1, ph1 in planets.items():
        for p2, ph2 in planets.items():
            if p1.value >= p2.value:
                continue
            aspect = get_aspect(ph1, ph2, orb_limit)
            if aspect is not None:
                out[PlanetTuple(p1, p2)] = aspect
    return out


def get_planet_dignity(planet: Planet, position: SignPosition) -> Dignity:
    sign = position.sign
    opposite = Sign((position.sign.value + 6) % 12)
    if RULERS[sign] == planet:
        return Dignity.DIGNITY
    if RULERS[opposite] == planet:
        return Dignity.DETRIMENT
    if planet in EXALTATIONS:
        if EXALTATIONS[planet][0] == sign:
            return Dignity.EXALTATION
        if EXALTATIONS[planet][0] == opposite:
            return Dignity.FALL
    return Dignity.NORMAL


def get_horoscope(date: datetime, lat: float, lon: float, orb_limit: float):
    ut = date_to_ut(date)
    asc = get_ascendant(ut, lat, lon)

    planets = dict()
    for planet in list(Planet):
        signPos = get_planet_pos(ut, planet, asc)
        dignity = get_planet_dignity(planet, signPos)
        planets[planet] = PlanetHoroscope(
            position=signPos,
            dignity=dignity,
            retrograde=signPos.speed < 0
        )

    aspects = get_all_aspects(planets, orb_limit)

    return Horoscope(
        planets=planets,
        aspects=aspects,
        ascending=asc,
    )


def print_horoscope(date: datetime, lat: float, lon: float, orb_limit: float):
    print(date.astimezone(None))
    horoscope = get_horoscope(date, lat, lon, orb_limit)
    divider = ['=' * 20] * 6

    # Planets
    table = [['Planet', 'Sign', 'House', 'Dignity', 'Angle', 'Speed', ]]
    table.append(divider)
    for planet, signHoro in horoscope.planets.items():
        signPos = signHoro.position
        table.append([
            planet.name,
            signPos.sign.name,
            signPos.house.name,
            signHoro.dignity.name,
            f'{signPos.sign_angle:4.1f}°',
            f'{signPos.speed:+6.2f} deg/day',
        ])

    # Middle
    table.append([])
    table.append(divider)
    table.append(['Ascending', horoscope.ascending.name])
    table.append([])

    # Aspects
    table.append(['Planet 1', 'Planet 2', 'Aspect', 'Orb'])
    table.append(divider)
    for planets, aspectHoro in horoscope.aspects.items():
        table.append([
            planets.planet1.name,
            planets.planet2.name,
            aspectHoro.aspect.name,
            f'{aspectHoro.orb:4.1f}°'
        ])

    # Display
    for row in table:
        row = [f'{cell:<20}' for cell in row]
        print(''.join(row))
