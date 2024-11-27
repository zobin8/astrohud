"""Main entrypoint"""

from datetime import datetime
from datetime import timezone
from typing import Tuple
import click

from astrohud.chart.star.models import StarChart
from astrohud.chart.wheel.models import ClassicWheelChart
from astrohud.chart.wheel.models import ModernWheelChart
from astrohud.cli.util import print_horoscope
from astrohud.lib.ephemeris.const import HOUSE_SYSTEMS
from astrohud.lib.ephemeris.enums import Zodiac
from astrohud.lib.ephemeris.models import EpheDate
from astrohud.lib.ephemeris.models import EpheSettings
from astrohud.lib.horoscope.models import Horoscope


LATITUDE = 38.5595886
LONGITUDE = -121.754827
HOUSE_SYS_NAMES = ', '.join([f'{v} ({k})' for k, v in HOUSE_SYSTEMS.items()])
ZODIAC_NAMES = [z.name for z in list(Zodiac)]
STYLE_NAMES = {
    'classic': ClassicWheelChart,
    'modern': ModernWheelChart,
    'star': StarChart,
}


def default_settings(function):
    @click.option('-o', '--orb-limit', type=float, default=2, show_default=True, help='Maximum orb limit for aspects, in degrees.')
    @click.option('-c', '--conjunction-limit', type=float, default=5, show_default=True, help='Maximum orb limit for conjunction, in degrees.')
    @click.option('-l', '--location', type=float, nargs=2, default=(LATITUDE, LONGITUDE), help='Latitude, Longitude coordinates for location. Defaults to Davis, CA')
    @click.option(
        '--zodiac', default=Zodiac.PLANETARIUM.name, type=click.Choice(ZODIAC_NAMES, case_sensitive=False), show_default=True,
        help=f'Zodiac system to use. Can be: {",".join(ZODIAC_NAMES)}'
    )
    @click.option('--aspects/--no-aspects', default=True, is_flag=True, show_default=True, help='Calculate planetary aspects')
    @click.option(
        '--house-sys', default='P', type=click.Choice(HOUSE_SYSTEMS.keys(), case_sensitive=False), show_default=True,
        help=f'House system. Can be: {HOUSE_SYS_NAMES}'
    )
    def wrapper(orb_limit: float, conjunction_limit: float, location: Tuple[float, float], zodiac: str, aspects: bool, house_sys: bytes, **kwargs):
        if not aspects:
            orb_limit = -1
        settings = EpheSettings(
            orb_limit=orb_limit,
            conjunction_limit=conjunction_limit,
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
@click.option('-d', '--date', type=click.DateTime(), default=datetime.now(timezone.utc), help='Date to use. Defaults to now.')
@click.option('--save-img', type=click.Path(dir_okay=False, writable=True), multiple=True, help='If specified, save horoscope image to path.')
@click.option('--background', type=click.Path(dir_okay=False, writable=True), multiple=True, help='If specified, overlay horoscope over image.')
@click.option('--background-shift', type=float, multiple=True, help='If specified, percentile to shift the background overlay')
@click.option('--style', type=click.Choice(STYLE_NAMES.keys(), case_sensitive=False), default='modern', help='Printed chart style.')
@default_settings
def horo(settings: EpheSettings, date: datetime, save_img: Tuple[str], background: Tuple[str], background_shift: Tuple[float], style: str):
    date = date.astimezone(timezone.utc)

    horo = Horoscope(ed=EpheDate(date), settings=settings)
    print(date.astimezone(None))
    print_horoscope(horo)

    chart_cls = STYLE_NAMES[style]

    if save_img:
        chart = chart_cls(horo)
        chart.finish()
        img = chart.img

        for i, save_path in enumerate(save_img):
            img_i = img
            shift = 0
            if (len(background_shift) > i):
                shift = background_shift[i]
            if len(background) > i:
                img_i = chart.overlay_image(background[i], shift)
            img_i.save(save_path)


if __name__ == '__main__':
    main()
