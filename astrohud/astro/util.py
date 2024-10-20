from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import swisseph as swe

from astrohud.astro.const import ASPECT_DEGREES
from astrohud.astro.const import EXALTATIONS
from astrohud.astro.const import RULERS
from astrohud.astro.enums import Dignity
from astrohud.astro.enums import Planet
from astrohud.astro.enums import Zodiac
from astrohud.astro.model import AspectHoroscope
from astrohud.astro.model import Horoscope
from astrohud.astro.model import HoroscopeSettings
from astrohud.astro.model import PlanetHoroscope
from astrohud.astro.model import PlanetTuple
from astrohud.astro.model import SignPosition
from astrohud.constellations.models import SignSplitter
from astrohud.ephemeris.models import EpheDate
from astrohud.ephemeris.models import HouseSplitter


def get_planet_pos(ut: float, planet: Planet, signs: SignSplitter, houses: HouseSplitter, zodiac: Zodiac) -> SignPosition:
    flags = swe.FLG_SPEED
    if zodiac == Zodiac.SIDEREAL:
        flags |= swe.FLG_SIDEREAL

    results, flags = swe.calc_ut(ut, planet.value, flags=flags)
    ra = results[0]
    dec = results[1]
    speed = results[3]

    sign = signs.split(ra, dec)
    house = houses.split(ra, dec)

    return SignPosition(
        abs_angle=ra,
        sign=sign,
        speed=speed,
        house=house,
        declination=dec,
    )


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


def get_planet_dignity(planet: Planet, position: SignPosition, signs: SignSplitter) -> Dignity:
    sign = position.sign
    opposite = signs.split(position.abs_angle + 180, -position.declination)
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
    ed = EpheDate(date)
    signs = SignSplitter(ed.obliquity, settings.zodiac)
    cusps = HouseSplitter(ed.ut, settings)

    planets = dict()
    for planet in list(Planet):
        signPos = get_planet_pos(ed.ut, planet, signs, cusps, settings.zodiac)
        dignity = get_planet_dignity(planet, signPos, signs)
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
        ascending=cusps.get_ascendant(signs),
        cusps={v: k for k, v in cusps.ring.items()},
        signs={v: k for k, v in signs.ring[0].ring.items()},
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
