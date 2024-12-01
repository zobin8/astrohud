"""Controllers for the horoscope namespace"""

from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict

from flask_restx import Namespace
from flask_restx import Resource

from astrohud.chart.styles.const import CHART_STYLE_CLASSES
from astrohud.chart.styles.const import CHART_STYLE_DESCRIPTIONS
from astrohud.chart.renderer.json.models import JsonRenderer
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
from astrohud.restapi._base.decorators import input_schema

from .models import Option
from .schema import horo_settings
from .schema import horoscope
from .schema import register_schema
from .schema import settings_options


api = Namespace('horo', description='Create horoscopes')
register_schema(api)


@api.route('/options')
class Options(Resource):
    """Get horoscope options"""

    @api.marshal_with(settings_options)
    def get(self) -> Dict[str, Any]:
        """List available options"""
        return dict(
            planets=Option.make_options(PLANET_DESCRIPTIONS),
            zodiac=Option.make_options(ZODIAC_DESCRIPTIONS),
            house_sys=Option.make_options(HOUSE_SYS_DESCRIPTIONS),
            style=Option.make_options(CHART_STYLE_DESCRIPTIONS),
        )


@api.route('/chart')
class Chart(Resource):
    """Chart horoscope"""

    @api.marshal_with(horoscope)
    @input_schema(api, horo_settings)
    def post(
        self,
        orb_limit: float,
        conjunction_limit: float,
        zodiac: str,
        house_sys: str,
        
        latitude: float,
        longitude: float,
        date: str,
        style: str,
    ):
        """Get a horoscope"""
        
        init_ephe()

        settings = EpheSettings(
            orb_limit=orb_limit,
            conjunction_limit=conjunction_limit,
            location=(latitude, longitude),
            zodiac=getattr(Zodiac, zodiac),
            house_sys=bytes(getattr(HouseSystem, house_sys).value, 'latin1'),
        )

        date = datetime.fromisoformat(date)
        date = date.astimezone(timezone.utc)

        horo = Horoscope(ed=EpheDate(date), settings=settings)

        chart_cls = CHART_STYLE_CLASSES[style]
        chart = chart_cls(horo)
        render = JsonRenderer(chart)
        render.draw_all()

        return dict(
            planets={k.name: v for k, v in horo.planets.items()},
            aspects={str(k): v for k, v in horo.aspects.items()},
            ascending=horo.ascending,
            chart=render.json
        )
