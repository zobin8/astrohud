"""Controllers for the horoscope namespace"""

from flask_restx import Namespace
from flask_restx import Resource
from datetime import datetime
from datetime import timezone

from astrohud.chart.charts.const import CHART_STYLE_CLASSES
from astrohud.chart.charts.const import CHART_STYLE_DESCRIPTIONS
from astrohud.chart.charts.enums import ChartStyle
from astrohud.lib.ephemeris.const import HOUSE_SYS_DESCRIPTIONS
from astrohud.lib.ephemeris.const import PLANET_DESCRIPTIONS
from astrohud.lib.ephemeris.const import ZODIAC_DESCRIPTIONS
from astrohud.lib.ephemeris.enums import HouseSystem
from astrohud.lib.ephemeris.enums import Zodiac
from astrohud.lib.ephemeris.models import EpheDate
from astrohud.lib.ephemeris.models import EpheSettings
from astrohud.lib.ephemeris.models import init_ephe
from astrohud.lib.horoscope.models import Horoscope
from astrohud.lib.horoscope.models import Horoscope


from .models import Option
from .schema import horoscope
from .schema import register_schema
from .schema import settings_options


api = Namespace('horo', description='Create horoscopes')
register_schema(api)


@api.route('/settings')
class Settings(Resource):
    """Get horoscope settings"""

    @api.marshal_with(settings_options)
    def get(self):
        """List available options"""
        return dict(
            planets=Option.make_options(PLANET_DESCRIPTIONS),
            zodiac=Option.make_options(ZODIAC_DESCRIPTIONS),
            house_sys=Option.make_options(HOUSE_SYS_DESCRIPTIONS),
            style=Option.make_options(CHART_STYLE_DESCRIPTIONS),
        )


@api.route('/')
class Horo(Resource):
    """Get horoscope"""

    @api.marshal_with(horoscope)
    def get(self):
        """Get a horoscope"""
        init_ephe()

        settings = EpheSettings(
            orb_limit=2,
            conjunction_limit=5,
            location=(38.5616433, -121.6265455),
            zodiac=Zodiac.PLANETARIUM,
            house_sys=bytes('P', 'latin1'),
        )

        date = datetime.now(timezone.utc)
        date = date.astimezone(timezone.utc)

        horo = Horoscope(ed=EpheDate(date), settings=settings)
        horo.planets = {k.name: v for k, v in horo.planets.items()}
        horo.aspects = {str(k): v for k, v in horo.aspects.items()}
        return horo
