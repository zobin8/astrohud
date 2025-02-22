"""Schema for the horo endpoints"""

from flask_restx import fields
from flask_restx import Model
from flask_restx import Namespace


# Settings options

option = Model('Option', dict(
    value=fields.String(),
    description=fields.String(),
))

settings_options = Model('SettingsOptions', dict(
    planets=fields.List(fields.Nested(option)),
    zodiac=fields.List(fields.Nested(option)),
    house_sys=fields.List(fields.Nested(option)),
    style=fields.List(fields.Nested(option)),
))

horo_settings = Model('HoroSettings', dict(
    orb_limit=fields.Float(),
    conjunction_limit=fields.Float(),
    zodiac=fields.String(),
    house_sys=fields.String(),
    
    latitude=fields.Float(),
    longitude=fields.Float(),
    date=fields.DateTime(),

    style=fields.String(),
))

# Horoscope

sign_pos = Model('SignPosition', dict(
    abs_angle=fields.Float(),
    sign=fields.String(attribute='sign.name'),
    declination=fields.Float(),
    speed=fields.Float(),
    house=fields.String(attribute='house.name'),
))

planet_horo = Model('PlanetHoroscope', dict(
    position=fields.Nested(sign_pos),
    dignity=fields.String(attribute='dignity.name'),
    retrograde=fields.Boolean(),
    score=fields.Float(),
))

aspect_horo = Model('AspectHoroscope', dict(
    aspect=fields.String(attribute='aspect.name'),
    orb=fields.Float(),
))

planets = Model('Planets', {
    '*': fields.Wildcard(fields.Nested(planet_horo)),
})

aspects = Model('Aspects', {
    '*': fields.Wildcard(fields.Nested(aspect_horo)),
})

horoscope = Model('Horoscope', dict(
    planets=fields.Nested(planets),
    ascending=fields.Nested(sign_pos),
    aspects=fields.Nested(aspects),
    chart=fields.Raw(),
))


def register_schema(api: Namespace):
    """Register schema with the api"""
    api.add_model(option.name, option)
    api.add_model(settings_options.name, settings_options)
    api.add_model(horo_settings.name, horo_settings)
    api.add_model(sign_pos.name, sign_pos)
    api.add_model(planet_horo.name, planet_horo)
    api.add_model(aspect_horo.name, aspect_horo)
    api.add_model(planets.name, planets)
    api.add_model(aspects.name, aspects)
    api.add_model(horoscope.name, horoscope)