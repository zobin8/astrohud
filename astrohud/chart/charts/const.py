"""Constants for different charts"""

from astrohud.chart.charts.wheel.models import WheelChart
from astrohud.chart.charts.wheel.models import ModernWheelChart
from astrohud.chart.charts.star.models import StarChart

from .enums import ChartStyle


CHART_STYLE_CLASSES = {
    ChartStyle.CLASSIC_WHEEL.name: WheelChart,
    ChartStyle.MODERN_WHEEL.name: ModernWheelChart,
    ChartStyle.STAR.name: StarChart,
}


CHART_STYLE_DESCRIPTIONS = {
    ChartStyle.CLASSIC_WHEEL.name: 'A classic wheel chart. Popular for natal charts.',
    ChartStyle.MODERN_WHEEL.name: 'A wheel chart. Aspects are rendered as bridged segments with tooltips.',
    # TODO: Re-enable when Star chart is ready
    # ChartStyle.STAR.name: 'A star-shaped projection map. WIP',
}