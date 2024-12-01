"""Schema for the horo endpoints"""

from flask_restx import fields
from flask_restx import Model

# Option
option = Model('Option', dict(
    value=fields.String(),
    description=fields.String(),
))

# List of all options for each setting
settings_options = Model('SettingsOptions', dict(
    planets=fields.List(fields.Nested(option)),
    zodiac=fields.List(fields.Nested(option)),
    house_sys=fields.List(fields.Nested(option)),
    style=fields.List(fields.Nested(option)),
))