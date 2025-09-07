from marshmallow import Schema, fields
from marshmallow.validate import Length

from app.web.schemes import OkResponseSchema


class ThemeSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)


class ListThemeSchema(Schema):
    themes = fields.Nested(ThemeSchema, many=True)


class ListThemeResponseSchema(OkResponseSchema):
    data = fields.Nested(ListThemeSchema)


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested(AnswerSchema, many=True, required=True, validate=Length(min=2))


class QuestionAddResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested(AnswerSchema, many=True, required=True, validate=Length(min=2))


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)


class ListQuestionQuerySchema(Schema):
    theme_id = fields.Int(required=False)


class ListQuestionResponseSchema(OkResponseSchema):
    data = fields.Nested(ListQuestionSchema)