"""Controllers for the horoscope namespace"""

from flask_restx import Namespace
from flask_restx import Resource

from astrohud.chart.charts.const import CHART_STYLE_DESCRIPTIONS
from astrohud.lib.ephemeris.const import HOUSE_SYS_DESCRIPTIONS
from astrohud.lib.ephemeris.const import ZODIAC_DESCRIPTIONS
from astrohud.lib.ephemeris.enums import Planet


api = Namespace('horo', description='Create horoscopes')


@api.route('/options')
class Options(Resource):
    """Get horoscope options"""

    def get(self):
        """List available options"""
        return dict(
            planets={p.name: p.name for p in Planet},
            zodiac=ZODIAC_DESCRIPTIONS,
            house_sys=HOUSE_SYS_DESCRIPTIONS,
            style=CHART_STYLE_DESCRIPTIONS,
        )