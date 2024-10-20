"""Main entrypoint"""

from datetime import datetime
from datetime import timezone
from typing import Tuple
import click
import json

from astrohud.lib.search.util import find_datetime_range
from astrohud.cli.util import print_horoscope
from astrohud.cli.util import print_range
from astrohud.lib.ephemeris.const import HOUSE_SYSTEMS
from astrohud.lib.ephemeris.enums import Zodiac
from astrohud.lib.ephemeris.models import EpheDate
from astrohud.lib.ephemeris.models import EpheSettings
from astrohud.gui.util import draw_horoscope
from astrohud.gui.util import overlay_image
from astrohud.lib.horoscope.models import Horoscope


LATITUDE = 38.5595886
LONGITUDE = -121.754827
HOUSE_SYS_NAMES = ', '.join([f'{v} ({k})' for k, v in HOUSE_SYSTEMS.items()])
ZODIAC_NAMES = [z.name for z in list(Zodiac)]


def default_settings(function):
    @click.option('-o', '--orb-limit', type=float, default=2, show_default=True, help='Maximum orb limit for aspects, in degrees.')
    @click.option('-l', '--location', type=float, nargs=2, default=(LATITUDE, LONGITUDE), help='Latitude, Longitude coordinates for location. Defaults to Davis, CA')
    @click.option(
        '--zodiac', default=Zodiac.IAU.name, type=click.Choice(ZODIAC_NAMES, case_sensitive=False), show_default=True,
        help=f'Zodiac system to use. Can be: {",".join(ZODIAC_NAMES)}'
    )
    @click.option('--aspects/--no-aspects', default=True, is_flag=True, show_default=True, help='Calculate planetary aspects')
    @click.option(
        '--house-sys', default='P', type=click.Choice(HOUSE_SYSTEMS.keys(), case_sensitive=False), show_default=True,
        help=f'House system. Can be: {HOUSE_SYS_NAMES}'
    )
    def wrapper(orb_limit: float, location: Tuple[float, float], zodiac: str, aspects: bool, house_sys: bytes, **kwargs):
        if not aspects:
            orb_limit = -1
        settings = EpheSettings(
            orb_limit=orb_limit,
            location=location,
            zodiac=getattr(Zodiac, zodiac.upper()),
            house_sys=bytes(house_sys, 'latin1'),
        )
        return function(settings=settings, **kwargs)
    
    wrapper.__name__ = function.__name__
    return wrapper


@click.group()
def main():
    pass


@main.command()
@click.option('-s', '--start-date', type=click.DateTime(), required=True, help='Date to start searching.')
@click.option('-e', '--end-date', type=click.DateTime(), required=True, help='Date to stop searching.')
@click.option('--day-filter', type=str, default=None, help='JSON filter file to pick the day (planet horoscopes)')
@click.option('--time-filter', type=str, default=None, help='JSON filter file to pick the time (aspects, ascending, etc.)')
@default_settings
def find(settings: EpheSettings, start_date: datetime, end_date: datetime, day_filter: str, time_filter: str):
    start_date = start_date.astimezone(timezone.utc)
    end_date = end_date.astimezone(timezone.utc)

    if day_filter:
        with open(day_filter) as f:
            day_filter = json.load(f)
    if time_filter:
        with open(time_filter) as f:
            time_filter = json.load(f)

    ranges = find_datetime_range(
        start_date=start_date,
        end_date=end_date,
        day_filter=day_filter or dict(),
        time_filter=time_filter or dict(),
        settings=settings,
    )

    for range in ranges:
        print(range[0].astimezone(None).isoformat() + ' --- ' + range[1].astimezone(None).isoformat())
        print_range(
            start_date=range[0],
            end_date=range[1],
            step=range[2],
            settings=settings,
        )
        print()


@main.command()
@click.option('-d', '--date', type=click.DateTime(), default=datetime.now(timezone.utc), help='Date to use. Defaults to now.')
@click.option('--save-img', type=click.Path(dir_okay=False, writable=True), multiple=True, help='If specified, save horoscope image to path.')
@click.option('--background', type=click.Path(dir_okay=False, writable=True), multiple=True, help='If specified, overlay horoscope over image.')
@default_settings
def horo(settings: EpheSettings, date: datetime, save_img: Tuple[str], background: Tuple[str]):
    date = date.astimezone(timezone.utc)

    horo = Horoscope(ed=EpheDate(date), settings=settings)
    print(date.astimezone(None))
    print_horoscope(horo)

    if save_img:
        img = draw_horoscope(horo)
        for i, save_path in enumerate(save_img):
            img_i = img
            if len(background) > i:
                img_i = overlay_image(background[i], img_i)
            img_i.save(save_path)


if __name__ == '__main__':
    main()
