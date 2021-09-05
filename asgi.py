from typing import Optional

import httpx
from fastapi import Body
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Header
from fastapi.requests import Request
from fastapi.responses import Response

import db
from methods import getMe
from methods import getWebhookInfo
from methods import telegram_client
from methods import WebhookInfo
from methods import setWebhook
from methods import sendMessage
from methods import SendMessageRequest
from type import Update
from config import settings
from lessons import task_3
from users import gen_random_name
from users import get_user
from util import apply_cache_headers
from util import authorize
from util import hide_webhook_secret
from util import safe
from util import static_response

app = FastAPI()

Telegram = Depends(telegram_client)

@app.get("/tg/about")
async def _(client: httpx.AsyncClient = Telegram):
    user = await getMe(client)
    return user


@app.get("/tg/webhook")
async def _(client: httpx.AsyncClient = Telegram):
    whi = await getWebhookInfo(client)
    hide_webhook_secret(whi)
    return whi


@app.post("/tg/webhook")
async def _(
    client: httpx.AsyncClient = Telegram,
    whi: WebhookInfo = Body(...),
    authorization: str = Header(""),
):
    authorize(authorization)

    whi.url = f"{whi.url}{settings.webhook_path}"
    webhook_set = await setWebhook(client, whi)

    whi = await getWebhookInfo(client)
    hide_webhook_secret(whi)

    return {
        "ok": webhook_set,
        "webhook": whi,
    }


@app.post(settings.webhook_path)
@safe
async def _(
    client: httpx.AsyncClient = Telegram,
    update: Update = Body(...),
):
    await sendMessage(
        client,
        SendMessageRequest(
            chat_id=update.message.chat.id,
            reply_to_message_id=update.message.message_id,
            text=task_3(update.message.text),
        ),
    )


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