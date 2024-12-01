"""Decorators used throughout the restapi module"""

from typing import Callable
from functools import wraps

from flask_restx import Model
from flask_restx import Api
from flask import request


def input_schema(api: Api, schema: Model):
    """Make an endpoint use a schema as an input to the request body"""
    def decorator(func: Callable):
        """Decorator around function"""
        @wraps(func)
        @api.expect(schema, validate=True)
        def wrapper(*args, **kwargs):
            """Wrap function and call with arguments from schema"""
            extra_kwargs = request.json
            return func(*args, **extra_kwargs, **kwargs)

        return wrapper

    return decorator