from hashlib import sha256

from aiohttp.web_exceptions import HTTPForbidden
from aiohttp_session import new_session

from aiohttp_apispec import request_schema, response_schema, docs

from app.admin.schemes import AdminSchema, AdminSchemaResponse
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response, error_json_response


class AdminLoginView(View):
    @docs(
        tags=["POST_view"],
        summary="Post login/password",
        description="login admin and send cookies to him"
    )
    @request_schema(AdminSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        data = await self.request.json()
        login = data["email"]
        password = data["password"]
        user = await self.store.admins.get_by_email(login)
        if user is None:
            raise HTTPForbidden
        hashed_password = sha256(password.encode()).hexdigest()
        if user.password == hashed_password:
            session = await new_session(self.request)
            session["admin"] = {
                "id": user.id,
                "email": user.email
            }
        return json_response(data=AdminSchemaResponse().dump(user))


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(
        tags=["GET_view"],
        summary="Get current user",
        description="Get current user by cookies"
    )
    @response_schema(
        OkResponseSchema, 200
    )
    async def get(self):
        try:
            user_session = await self.get_session()
            user_id = user_session.get("admin")["id"]
            user_email = user_session.get("admin")["email"]
        # except TypeError as e:
        #     raise HTTPUnauthorized
        except Exception as e:
            print(f" New exception = {e}")
            raise error_json_response(
                http_status=500,
                message=f"Error in view admin{e}"
            )
        return json_response(data={
            "id": user_id,
            "email": user_email
        })