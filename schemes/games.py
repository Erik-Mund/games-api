from marshmallow import Schema, fields, validate
from schemes.genres import GenreResponseSchema

class PostGameSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(max=200), metadata={"example":"TestGame"})
    release_year = fields.Integer()
    genre = fields.List(fields.Integer, metadata={"description":"insert genres' ids"})
    platform = fields.String(validate=validate.Length(max=300))
    summary = fields.String(validate=validate.Length(max=5000))
    price = fields.Integer()

class PutGameSchema(Schema):
    title = fields.String(validate=validate.Length(max=200), metadata={"example":"TestGame"})
    release_year = fields.Integer()
    genre = fields.List(fields.Integer, metadata={"description":"insert genres' ids"})
    platform = fields.String(validate=validate.Length(max=300))
    summary = fields.String(validate=validate.Length(max=5000))
    price = fields.Integer()

class GameResponseSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    genres = fields.List(fields.Nested(GenreResponseSchema))