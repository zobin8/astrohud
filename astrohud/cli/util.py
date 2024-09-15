from datetime import datetime
from datetime import timedelta

from astrohud.astro.model import Horoscope
from astrohud.astro.util import get_all_horoscopes
from astrohud.astro.util import approx_filter


def print_range(
    start_date: datetime,
    end_date: datetime,
    step: timedelta,
    lat: float,
    lon: float,
    orb_limit: float,
):
    all_horos = get_all_horoscopes(
        start_date=start_date,
        end_date=end_date,
        step=step,
        lat=lat,
        lon=lon,
        orb_limit=orb_limit,
    )

    last_approx = None
    for date, horo in all_horos:
        approx = approx_filter(horo.to_json())
        if approx != last_approx:
            print_horoscope(date, horo)
            print()
            last_approx = approx


def print_horoscope(date: datetime, horoscope: Horoscope):
    print(date.astimezone(None))
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
