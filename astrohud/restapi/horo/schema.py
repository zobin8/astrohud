"""Schema for horoscopes"""

from marshmallow import Schema
from marshmallow import fields


class OptionChoiceSchema(Schema):
    """Schema for listing option choices"""
    planets = fields.Dict(fields.String, fields.String)
    zodiac = fields.Dict(fields.String, fields.String)
    house_sys = fields.Dict(fields.String, fields.String)
    style = fields.Dict(fields.String, fields.String)
