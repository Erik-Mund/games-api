from marshmallow import Schema, fields, validate
from GameBaseAPI.schemes.genres import GenreResponseSchema
from datetime import datetime

class PostGameSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(max=200), metadata={"example":"TestGame"})
    release_year = fields.Integer(validate=validate.Range(min=1960, max=9999), metadata={"example":datetime.now().year})
    genres = fields.List(fields.String, metadata={"description":"insert genres' names", "example":["Action"]})
    platform = fields.String(load_default="PC", validate=validate.Length(max=300), metadata={"example":"PC"})
    summary = fields.String(load_default="No summary", validate=validate.Length(max=5000))
    price = fields.Integer()

class PutGameSchema(Schema):
    title = fields.String(validate=validate.Length(max=200), metadata={"example":"TestGame"})
    release_year = fields.Integer(validate=validate.Range(min=1960, max=9999), metadata={"example":datetime.now().year})
    genres = fields.List(fields.String, metadata={"description":"insert genres' names", "example":["Action"]})
    platform = fields.String(validate=validate.Length(max=300), metadata={"example":"PC"})
    summary = fields.String(validate=validate.Length(max=5000))
    price = fields.Integer()

class GameResponseSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    genres = fields.List(fields.Nested(GenreResponseSchema))