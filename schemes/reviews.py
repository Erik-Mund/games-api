from marshmallow import Schema, fields, validate

class PostReviewSchema(Schema):
    #game_id = fields.Integer(required=True, metadata={"description": "id of the game reviewed"})
    score = fields.Integer(strict=True, required=True, validate=validate.Range(min=1, max=5), metadata={"description":"minimum 1, maximum 5"})
    comment = fields.String(validate=validate.Length(max=400))

class PutReviewSchema(Schema):
    score = fields.Integer(strict=True, validate=validate.Range(min=1, max=5), metadata={"description":"minimum 1, maximum 5"})
    comment = fields.String(validate=validate.Length(max=400))