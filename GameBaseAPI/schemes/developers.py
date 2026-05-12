from marshmallow import Schema, fields, validate

class PostDeveloperSchema(Schema):
    studio_name = fields.String(required=True, validate=validate.Length(max=150), metadata={"example":"ExampleDeveloper"})

class PutDeveloperSchema(Schema):
    studio_name = fields.String(required=True, validate=validate.Length(max=150), metadata={"example":"ExampleDeveloper"})