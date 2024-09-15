from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import List
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


def get_house(position: float, cusps: Dict[House, float]) -> House:
    best_house = None
    best_dist = 360
    for house, cusp in cusps.items():
        angle = position - cusp
        if angle < 0:
            angle += 360
        if angle < best_dist:
            best_dist = angle
            best_house = house
    return best_house


def get_planet_pos(ut: float, planet: Planet, cusps: Dict[House, float]) -> SignPosition:
    results, flags = swe.calc_ut(ut, planet.value, flags=swe.FLG_SPEED)
    position=results[0]
    speed=results[3]

    sign, deg = get_sign(position)
    house = get_house(position, cusps)

    return SignPosition(
        abs_angle=position,
        sign=sign,
        sign_angle=deg,
        speed=speed,
        house=house,
    )


def get_cusps(ut: float, lat: float, lon: float) -> Tuple[Dict[House, float], Sign]:
    cusps, angles = swe.houses(ut, lat, lon, hsys=b'P')
    ascendant = angles[0]
    sign = get_sign(ascendant)[0]

    return {House(i + 1): c for i, c in enumerate(cusps)}, sign


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


def get_horoscope(date: datetime, lat: float, lon: float, orb_limit: float) -> Horoscope:
    ut = date_to_ut(date)
    cusps, asc = get_cusps(ut, lat, lon)

    planets = dict()
    for planet in list(Planet):
        signPos = get_planet_pos(ut, planet, cusps)
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
        cusps=cusps,
    )


def get_all_horoscopes(
    start_date: datetime,
    end_date: datetime,
    step: timedelta,
    lat: float,
    lon: float,
    orb_limit: float,
) -> List[Tuple[datetime, Horoscope]]:
    date = start_date
    out = []
    while date <= end_date:
        horo = get_horoscope(date, lat, lon, orb_limit)
        out.append((date, horo))
        date += step
    return out


def find_range(
    start_date: datetime,
    end_date: datetime,
    step: timedelta,
    lat: float,
    lon: float,
    orb_limit: float,
    filter: Dict[str, Any]
) -> List[Tuple[datetime, datetime, timedelta]]:
    all_horos = get_all_horoscopes(
        start_date=start_date,
        end_date=end_date,
        step=step,
        lat=lat,
        lon=lon,
        orb_limit=orb_limit,
    )

    match_ranges = []
    matched_last = False
    for date, horo in all_horos:
        matched = horo.match(filter)
        if matched:
            if matched_last:
                match_ranges[-1][1] = date
            else:
                match_ranges.append([date, date, step])

        matched_last = matched
        date += step
    return match_ranges


def find_datetime_range(
    start_date: datetime,
    end_date: datetime,
    lat: float,
    lon: float,
    orb_limit: float,
    day_filter: Dict[str, Any],
    time_filter: Dict[str, Any],
) -> List[Tuple[datetime, datetime, timedelta]]:
    day_ranges = find_range(
        start_date=start_date,
        end_date=end_date,
        step=timedelta(days=1),
        lat=lat,
        lon=lon,
        orb_limit=orb_limit,
        filter=day_filter
    )

    day_filter.update(time_filter)

    time_ranges = []
    for day_range in day_ranges:
        time_ranges += find_range(
            start_date=day_range[0] - timedelta(days=1),
            end_date=day_range[1] + timedelta(days=1),
            step=timedelta(minutes=15),
            lat=lat,
            lon=lon,
            orb_limit=orb_limit,
            filter=day_filter
        )

    return time_ranges


def approx_filter(item: Any) -> Any:
    if isinstance(item, float):
        return 0.0
    elif isinstance(item, dict):
        out = '('
        for k in sorted(item.keys()):
            out += f'k={approx_filter(item[k])},'
        out += ')'
        return out
    return str(item)
