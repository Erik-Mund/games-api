from marshmallow import Schema, fields, validate

class PostGenreSchema(Schema):
    name = fields.String(validate=validate.Length(max=100))

class GenreResponseSchema(Schema):
    name = fields.String()