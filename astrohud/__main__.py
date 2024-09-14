from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Tuple
import click
import json

from astrohud.astro.util import get_horoscope
from astrohud.astro.util import find_datetime_range
from astrohud.astro.util import print_horoscope
from astrohud.astro.util import print_range


LATITUDE = 38.5595886
LONGITUDE = -121.754827


@click.group()
@click.option('-o', '--orb', type=float, default=5, help='Maximum orb limit for aspects, in degrees.')
@click.option('-l', '--location', type=float, nargs=2, default=(LATITUDE, LONGITUDE), help='Latitude, Longitude coordinates for location. Defaults to Davis, CA')
@click.pass_context
def main(ctx: click.Context, **kwargs):
    ctx.ensure_object(dict)
    ctx.obj.update(kwargs)


@main.command()
@click.option('-s', '--start-date', type=click.DateTime(), required=True, help='Date to start searching.')
@click.option('-e', '--end-date', type=click.DateTime(), required=True, help='Date to stop searching.')
@click.option('--day-filter', type=str, default='{}', help='JSON filter to pick the day (planet horoscopes)')
@click.option('--time-filter', type=str, default='{}', help='JSON filter to pick the time (aspects, ascending, etc.)')
@click.pass_context
def find(ctx: click.Context, start_date: datetime, end_date: datetime, day_filter: str, time_filter: str):
    start_date = start_date.astimezone(timezone.utc)
    end_date = end_date.astimezone(timezone.utc)

    lat, lon = ctx.obj['location']
    ranges = find_datetime_range(
        start_date=start_date,
        end_date=end_date,
        lat=lat,
        lon=lon,
        orb_limit=ctx.obj['orb'],
        day_filter=json.loads(day_filter),
        time_filter=json.loads(time_filter),
    )

    for range in ranges:
        print(range[0].astimezone(None).isoformat() + ' --- ' + range[1].astimezone(None).isoformat())
        print_range(
            start_date=range[0],
            end_date=range[1],
            step=range[2],
            lat=lat,
            lon=lon,
            orb_limit=ctx.obj['orb'],
        )
        print()


@main.command()
@click.option('-d', '--date', type=click.DateTime(), default=datetime.now(timezone.utc), help='Date to use. Defaults to now.')
@click.pass_context
def horo(ctx: click.Context, date: datetime):
    date = date.astimezone(timezone.utc)
    lat, lon = ctx.obj['location']

    horo = get_horoscope(date, lat, lon, ctx.obj['orb'])
    print_horoscope(date, horo)


if __name__ == '__main__':
    main()
