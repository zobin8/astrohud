from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import List
import os
import math

import swisseph as swe
import pandas as pd

from astrohud.astro.const import ASPECT_DEGREES
from astrohud.astro.const import RULERS
from astrohud.astro.const import EXALTATIONS
from astrohud.astro.enums import Dignity
from astrohud.astro.enums import House
from astrohud.astro.enums import Planet
from astrohud.astro.enums import Sign
from astrohud.astro.model import AspectHoroscope
from astrohud.astro.model import Horoscope
from astrohud.astro.model import HoroscopeSettings
from astrohud.astro.model import PlanetHoroscope
from astrohud.astro.model import PlanetTuple
from astrohud.astro.model import SignPosition


CONSTELLATIONS: Dict[Sign, List[Tuple[float, float]]] = defaultdict(list)


def init_ephe():
    dirname = os.path.dirname(__file__)
    ephe_path = os.path.join(dirname, '../../submodules/swisseph/ephe')
    swe.set_ephe_path(ephe_path)

    constellation_path = os.path.join(dirname, '../data/constellations.csv')
    df = pd.read_csv(constellation_path)
    df['Angle'] = ((df.Seconds / 60 + df.Minutes) / 60 + df.Hours) * 15
    df['Sign'] = df.Sign.apply(lambda n: getattr(Sign, n.upper()))
    for _, row in df.iterrows():
        CONSTELLATIONS[row.Sign].append((row.Angle, row.Declination))


def celestial_to_ecliptic(celestial_x: float, celestial_y: float, obliquity: float) -> Tuple[float, float]:
    # Formula derived by:
    # 1. Converting to Cartesian (x=cosa cosb, y=sina cosb, z=sinb)
    # 2. Rotating across X axis
    # 3. Converting back to Spherical

    cos_cx = math.cos(math.radians(celestial_x))
    sin_cx = math.sin(math.radians(celestial_x))
    cos_cy = math.cos(math.radians(celestial_y))
    sin_cy = math.sin(math.radians(celestial_y))
    cos_ob = math.cos(-math.radians(obliquity))
    sin_ob = math.sin(-math.radians(obliquity))

    sin_ey = sin_ob * sin_cx * cos_cy + cos_ob * sin_cy
    ey = math.asin(sin_ey)

    cos_ex = cos_cx * cos_cy / math.cos(ey)
    ex_pos = cos_ob * sin_cx * cos_cy
    ex_neg = sin_ob * sin_cy
    ex = math.acos(cos_ex)
    if ex_neg > ex_pos:
        ex *= -1
    
    return math.degrees(ex), math.degrees(ey)


def get_iau_signs(ut: float) -> Dict[Sign, float]:
    results, _ = swe.calc_ut(ut, swe.ECL_NUT, 0)
    obliquity = results[0]

    out = dict()
    for sign, celestial_points in CONSTELLATIONS.items():
        points = [celestial_to_ecliptic(x, y, obliquity) for x, y in celestial_points]
        next_points = points[1:] + points[:0]
        for pt1, pt2 in zip(points, next_points):
            if (pt1[1] > 0) != (pt2[1] > 0):
                m = (pt1[1] - pt2[1]) / (pt1[0] - pt2[0])
                x = pt1[0] - pt1[1] / m
                if sign in out:
                    while x - out[sign] > 180:
                        x -= 360
                    while out[sign] - x > 180:
                        x += 360
                    if x > out[sign]:
                        break
                out[sign] = x

    return out

def get_signs(ut: float, settings: HoroscopeSettings) -> Dict[Sign, float]:
    if settings.iau:
        return get_iau_signs(ut)
    
    out = dict()
    for i in range(12):
        out[Sign(i)] = i * 30

    return out


def date_to_ut(date: datetime) -> float:
    assert date.tzinfo == timezone.utc
    date_tup = date.timetuple()[:6]
    et, ut = swe.utc_to_jd(*date_tup, swe.GREG_CAL)
    return ut


def split_deg(position: float, start_limits: Dict[Any, float]) -> Tuple[Any, float]:
    best_option = None
    best_dist = 360
    best_angle = 0
    for option, limit in start_limits.items():
        angle = (position - limit) % 360
        if angle < best_dist:
            best_dist = angle
            best_option = option
            best_angle = angle
    return best_option, best_angle


def get_planet_pos(ut: float, planet: Planet, signs: Dict[Sign, float], cusps: Dict[House, float], sidereal: bool) -> SignPosition:
    flags = swe.FLG_SPEED
    if sidereal:
        flags |= swe.FLG_SIDEREAL

    results, flags = swe.calc_ut(ut, planet.value, flags=flags)
    position=results[0]
    speed=results[3]

    sign, deg = split_deg(position, signs)
    house, _ = split_deg(position, cusps)

    return SignPosition(
        abs_angle=position,
        sign=sign,
        sign_angle=deg,
        speed=speed,
        house=house,
    )


def get_cusps(ut: float, signs: Dict[Sign, float], settings: HoroscopeSettings) -> Tuple[Dict[House, float], SignPosition]:
    flag_args = dict()
    if settings.sidereal:
        flag_args['flags'] = swe.FLG_SIDEREAL
    cusps, angles = swe.houses_ex(ut, settings.location[0], settings.location[1], hsys=settings.house_sys, **flag_args)
    ascendant = angles[0]
    sign, sign_angle = split_deg(ascendant, signs)

    signPos = SignPosition(
        abs_angle=ascendant,
        sign=sign,
        sign_angle=sign_angle,
        speed=0,
        house=House.IDENTITY_1,
    )

    return {House(i + 1): c for i, c in enumerate(cusps)}, signPos


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


def get_horoscope(date: datetime, settings: HoroscopeSettings) -> Horoscope:
    ut = date_to_ut(date)
    signs = get_signs(ut, settings)
    cusps, asc = get_cusps(ut, signs, settings)

    planets = dict()
    for planet in list(Planet):
        signPos = get_planet_pos(ut, planet, signs, cusps, settings.sidereal)
        dignity = get_planet_dignity(planet, signPos)
        planets[planet] = PlanetHoroscope(
            position=signPos,
            dignity=dignity,
            retrograde=signPos.speed < 0
        )

    aspects = dict()
    if settings.aspects:
        aspects = get_all_aspects(planets, settings.orb_limit)

    return Horoscope(
        planets=planets,
        aspects=aspects,
        ascending=asc,
        cusps=cusps,
        signs=signs,
    )


def get_all_horoscopes(
    start_date: datetime,
    end_date: datetime,
    step: timedelta,
    settings: HoroscopeSettings,
) -> List[Tuple[datetime, Horoscope]]:
    date = start_date
    out = []
    while date <= end_date:
        horo = get_horoscope(date, settings)
        out.append((date, horo))
        date += step
    return out


def find_range(
    start_date: datetime,
    end_date: datetime,
    step: timedelta,
    filter: Dict[str, Any],
    settings: HoroscopeSettings,
) -> List[Tuple[datetime, datetime, timedelta]]:
    all_horos = get_all_horoscopes(
        start_date=start_date,
        end_date=end_date,
        step=step,
        settings=settings,
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
    day_filter: Dict[str, Any],
    time_filter: Dict[str, Any],
    settings: HoroscopeSettings,
) -> List[Tuple[datetime, datetime, timedelta]]:
    day_ranges = find_range(
        start_date=start_date,
        end_date=end_date,
        step=timedelta(days=1),
        filter=day_filter,
        settings=settings,
    )

    day_filter.update(time_filter)

    time_ranges = []
    for day_range in day_ranges:
        time_ranges += find_range(
            start_date=day_range[0] - timedelta(days=1),
            end_date=day_range[1] + timedelta(days=1),
            step=timedelta(minutes=15),
            filter=day_filter,
            settings=settings
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
