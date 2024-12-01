"""JSON renderer"""

from enum import Enum
from typing import Any
from typing import Dict
from typing import List

from astrohud.chart._base.models import BaseCoord
from astrohud.chart._base.models import BaseRenderer
from astrohud.chart._base.models import BaseShape


class JsonRenderer(BaseRenderer):
    """Renderer using Pillow library"""
    shapes: List[Any]
    json: Dict[str, Any]

    def __init__(self, chart):
        """Constructor"""
        super().__init__(chart)
        self.shapes = []
        self.json = dict(
            width=chart.width,
            shapes=self.shapes,
        )

    # Overrides

    def draw_shape(self, shape: BaseShape):
        """Draw a shape"""
        shape_dict = dict(vars(shape))
        for key, value in shape_dict.items():
            if isinstance(value, BaseCoord):
                shape_dict[key] = tuple(self.chart.convert_coord(value).array)
            if isinstance(value, Enum):
                shape_dict[key] = str(value)

        self.shapes.append(dict(
            type=type(shape).__name__,
            **shape_dict,
        ))
        

    def finish(self):
        """Finish drawing"""
