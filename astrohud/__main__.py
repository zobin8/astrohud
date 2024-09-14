from astrohud.astro.util import print_horoscope
from datetime import datetime
from datetime import timezone
import click


LATITUDE = 38.5595886
LONGITUDE = -121.754827


@click.command()
@click.option('-d', '--date', type=click.DateTime(), default=datetime.now(timezone.utc), help='Date to use. Defaults to now')
def main(date: datetime):
    date = date.astimezone(timezone.utc)
    print_horoscope(date, LATITUDE, LONGITUDE, 1)


if __name__ == '__main__':
    main()