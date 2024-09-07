from astrohud.astro.util import print_horoscope
from datetime import datetime

date = datetime.utcnow()
LATITUDE = 38.5595886
LONGITUDE = -121.754827


print_horoscope(date, LATITUDE, LONGITUDE, 1)
