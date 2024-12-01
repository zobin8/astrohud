"""Controllers for the horoscope namespace"""

from flask_restx import Namespace
from flask_restx import Resource

from astrohud.chart.charts.const import CHART_STYLE_DESCRIPTIONS
from astrohud.lib.ephemeris.const import HOUSE_SYS_DESCRIPTIONS
from astrohud.lib.ephemeris.const import PLANET_DESCRIPTIONS
from astrohud.lib.ephemeris.const import ZODIAC_DESCRIPTIONS

from .models import Option
from .schema import option
from .schema import settings_options


api = Namespace('horo', description='Create horoscopes')
api.add_model(option.name, option)
api.add_model(settings_options.name, settings_options)


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
