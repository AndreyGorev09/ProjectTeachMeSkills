import httpx
from fastapi import Body
from fastapi import FastAPI
from fastapi import Header
from fastapi.requests import Request

from fastapi import Depends
from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

import os
import db
from lessons import task_3
from users import gen_random_name
from users import get_user
from util import apply_cache_headers
from util import authorize
from util import static_response


app = FastAPI()


token = os.getenv("TG_BOT_TOKEN")
url = f"https://api.telegram.org/bot{token}"
assert token, "no tg token provided"
print(f"token = {token!r}")


class Type(BaseModel):
    pass


class Response(Type):
    description: str = Field("")
    error_code: int = Field(0)
    ok: bool = Field(...)
    result: Any = Field(None)


class User(Type):
    id: int = Field(...)
    is_bot: bool = Field(...)
    first_name: str = Field(...)
    last_name: str = Field("")
    username: str = Field("")


class WebhookInfo(Type):
    url: str = Field(...)
    pending_update_count: int = Field(0)
    last_error_date: int = Field(0)
    last_error_message: str = Field("")


class GetMeResponse(Response):
    result: Optional[User] = Field(None)


class GetWebhookInfoResponse(Response):
    result: Optional[WebhookInfo] = Field(None)


class SetWebhookResponse(Response):
    result: bool = Field(False)






async def telegram_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(base_url=url) as client:
        yield client


rr_types_map = {
    "getMe": GetMeResponse,
    "getWebhookInfo": GetWebhookInfoResponse,
    "setWebhook": SetWebhookResponse,
}


async def api_call(
    client: httpx.AsyncClient, method: str, data: Optional[Type] = None
) -> Response:
    type = rr_types_map[method]
    payload = data.dict(exclude_unset=True) if data is not None else None
    response: httpx.Response = await client.post(f"/{method}", json=payload)
    result = type.parse_obj(response.json())

    return result


async def getMe(client: httpx.AsyncClient) -> User:
    response = await api_call(client, "getMe")
    return response.result


async def getWebhookInfo(client: httpx.AsyncClient) -> WebhookInfo:
    response = await api_call(client, "getWebhookInfo")
    return response.result


async def setWebhook(client: httpx.AsyncClient, whi: WebhookInfo) -> bool:
    response = await api_call(client, "setWebhook", data=whi)
    return response.result





Telegram = Depends(telegram_client)

@app.get("/tg/about")
async def _(client: httpx.AsyncClient = Telegram):
    user = await getMe(client)
    return user


@app.get("/tg/webhook")
async def _(client: httpx.AsyncClient = Telegram):
    whi = await getWebhookInfo(client)
    return whi


@app.post("/tg/webhook")
async def _(
    client: httpx.AsyncClient = Telegram,
    whi: WebhookInfo = Body(...),
    authorization: str = Header(""),
):
    authorize(authorization)
    webhook_set = await setWebhook(client, whi)
    whi = await getWebhookInfo(client)
    return {
        "ok": webhook_set,
        "webhook": whi,
    }


@app.get("/")
async def _(response: Response):
    apply_cache_headers(response)

    return static_response("index.html")


@app.get("/img")
async def _(response: Response):
    apply_cache_headers(response)

    return static_response("image.jpg")


@app.get("/js")
async def _(response: Response):
    apply_cache_headers(response)

    return static_response("index.js")


@app.post("/task/3")
async def _(name: Optional[str] = Body(default=None)):
    result = task_3(name)
    return {"data": {"greeting": result}}


@app.post("/task/4")
async def _(request: Request, response: Response, data: str = Body(...)):
    user = get_user(request) or gen_random_name()
    response.set_cookie("user", user)

    if data == "stop":
        number = await db.get_number(user)
    else:
        number = await db.add_number(user, int(data))

    return {"data": {"n": number}}