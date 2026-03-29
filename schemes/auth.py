from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, metadata={"example": "Password123"})

class TokenSchema(Schema):
    access_token = fields.String()
    refresh_token = fields.String()

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8), metadata={"description": "min 8 characters; 1 integer, 1 upper, 1 lower required", "example": "Password123"})
    name = fields.String(required=True)
