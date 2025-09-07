from marshmallow import Schema, fields


class AdminSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)


class AdminSchemaResponse(Schema):
    email = fields.Str(required=True)
    id = fields.Int(required=True, attribute="id")