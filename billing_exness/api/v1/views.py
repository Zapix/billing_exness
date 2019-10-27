# -*- coding: utf-8 -*-
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.schemas.openapi import AutoSchema


class ObtainAuthTokenSchema(AutoSchema):
    """
    Describes schema for obtain token view
    """

    def _get_request_body(self, path, method) -> dict:
        return {
            'content': {
                'application/json': {
                    "schema": {
                        'type': 'object',
                        'required': ['username', 'password'],
                        'properties': {
                            'username': {'type': 'string'},
                            'password': {'type': 'string'}
                        }
                    },
                }
            }
        }

    def _get_responses(self, path, method) -> dict:
        return {
            '200': {
                'description': 'auth token received',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'token': {'type': 'string'}
                        }
                    }
                }
            },
            '400': {
                'description': 'can`t receive auth token',
            }
        }


class ObtainAuthTokenWithInfo(ObtainAuthToken):
    schema = ObtainAuthTokenSchema()
