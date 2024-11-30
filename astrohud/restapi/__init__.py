"""Submodule for REST API"""

from flask import Flask
from flask_restx import Api

from astrohud.restapi.horo.controllers import api as horo_api


api = Api(
    title='AstroHud API',
    description='Work with astral data',
)

api.add_namespace(horo_api)

flask_app = Flask(__name__)
api.init_app(flask_app)
