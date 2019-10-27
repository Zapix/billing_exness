# -*- coding: utf-8 -*-
from typing import List

from rest_framework.schemas.openapi import SchemaGenerator, AutoSchema


class BillingExnessSchemaGenerator(SchemaGenerator):

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public=False)
        security = self.get_security_schemes()

        if security:
            schema['components'] = {
                'securitySchemes': security
            }

        return schema

    def get_security_schemes(self):
        return {
            'ApiKeyAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name':  'Authorization'
            }
        }

    def has_view_permissions(self, path, method, view):
        return True


class SecurityRequiredSchema(AutoSchema):

    def get_operation(self, path, method) -> dict:
        operation = super().get_operation(path, method)

        operation['security'] = self.get_security()

        return operation

    def get_security(self) -> List[dict]:
        return [
            {'ApiKeyAuth': []}
        ]
