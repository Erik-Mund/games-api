from marshmallow import Schema, fields, validate


class PutMeSchema(Schema):
    name = fields.String(metadata={"example": "username1"})
    old_password = fields.String(metadata={"example": "Password123", "description": "required when changing password"})
    password = fields.String(validate=validate.Length(min=8), metadata={"example": "Password1234"})

class DeleteMeSchema(Schema):
    password = fields.String(metadata={"example": "Password123"})