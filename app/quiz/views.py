from aiohttp_apispec import request_schema, response_schema,querystring_schema, docs
from aiohttp.web_exceptions import HTTPNotFound, HTTPBadRequest, HTTPConflict

from app.quiz.models import Answer
from app.quiz.schemes import ThemeSchema, ListThemeResponseSchema, ListThemeSchema, QuestionSchema, ListQuestionSchema, \
    QuestionAddResponseSchema, ListQuestionResponseSchema, ListQuestionQuerySchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response, error_json_response


# TODO: добавить проверку авторизации для этого View
class ThemeAddView(AuthRequiredMixin, View):
    # TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем
    @docs(
        tags=["POST", "Themes"],
        summary="Add new theme",
        description="Добавление новых тем"
    )
    @request_schema(ThemeSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        self.data["title"] = (await self.request.json())[
            "title"
        ]
        existing_themes = await self.store.quizzes.list_themes()
        for each in existing_themes:
            if self.data["title"] == each.title:
                return error_json_response(
                    http_status=409,
                    status="conflict",
                    message="Тема уже судществует"
                )

        theme = await self.store.quizzes.create_theme(title=self.data["title"])
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @docs(
        tags=["GET", "Themes"],
        summary="Get all themes",
        description="Получить список всех тем"
    )
    @response_schema(ListThemeResponseSchema, 200)
    async def get(self):
        list_themes = await self.store.quizzes.list_themes()
        return json_response(data=ListThemeSchema().dump({"themes": list_themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @docs(
        tags=["question add"],
        summary="Additing new question"
    )
    @request_schema(QuestionSchema)
    @response_schema(QuestionAddResponseSchema, 200)
    async def post(self):
        theme_id = (await self.request.json())["theme_id"]
        self.data["theme_id"] = theme_id
        theme = await self.store.quizzes.get_theme_by_id(id_=theme_id)

        if not theme:
            raise HTTPNotFound

        answers = (await self.request.json())["answers"]
        self.data["answers"] = answers
        number_correct_answer = sum(answer["is_correct"] for answer in answers)  # Generator
        if number_correct_answer != 1:
            raise HTTPBadRequest

        title = (await self.request.json())["title"]
        self.data["title"] = title
        existed_question = await self.store.quizzes.get_question_by_title(title=title)
        if existed_question:
            raise HTTPConflict

        question = await self.store.quizzes.create_question(
            title=title,
            theme_id=theme_id,
            answers=[
                Answer(
                    title=answer["title"],
                    is_correct=answer["is_correct"]

                ) for answer in answers]
        )

        data = QuestionAddResponseSchema().dump(question)
        return json_response(data=data)


class QuestionListView(AuthRequiredMixin, View):
    @docs(
        tags=["question list"],
        summary="Отобразить все воросы"
    )
    @querystring_schema(ListQuestionQuerySchema)
    @response_schema(ListQuestionResponseSchema, 200)
    async def get(self):
        theme_id = self.request.query.get("theme_id")
        if theme_id is None:
            questions_list = await self.store.quizzes.list_questions()
        else:
            theme_id = int(theme_id)
            questions_list = await self.store.quizzes.list_questions(theme_id=theme_id)
        return json_response(data=ListQuestionSchema().dump({"questions": questions_list}))