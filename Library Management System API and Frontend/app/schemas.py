from marshmallow import Schema, fields, ValidationError

class BookSchema(Schema):
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    published_date = fields.Date()
    isbn = fields.Str(required=True)
    availability = fields.Bool(missing=True)

    @staticmethod
    def validate_isbn(isbn):
        # Example ISBN validation logic
        if len(isbn) != 10 and len(isbn) != 13:
            raise ValidationError('Invalid ISBN. Must be 10 or 13 characters.')

class MemberSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    membership_date = fields.Date()