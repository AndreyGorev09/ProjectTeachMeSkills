from typing import Any
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field

from util import update_forward_refs


class Type(BaseModel):
    pass


class Request(Type):
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


class Chat(Type):
    id: int = Field(...)
    type: str = Field(...)
    title: str = Field("")
    username: str = Field("")


@update_forward_refs
class Message(Type):
    chat: Chat = Field(...)
    date: int = Field(...)
    edit_date: int = Field(0)
    from_: Optional[User] = Field(None)
    message_id: int = Field(...)
    reply_to_message: Optional["Message"] = None
    text: str = Field("")

    class Config:
        fields = {
            "from_": "from",
        }


class Update(Type):
    update_id: int = Field(...)
    message: Optional[Message] = Field(None)
    edited_message: Optional[Message] = Field(None)


class WebhookInfo(Type):
    url: str = Field(...)
    pending_update_count: int = Field(0)
    last_error_date: int = Field(0)
    last_error_message: str = Field("")


class SendMessageRequest(Request):
    chat_id: Union[int, str] = Field(...)
    disable_notification: bool = Field(False)
    parse_mode: Optional[str] = Field(None)
    reply_to_message_id: Optional[int] = Field(None)
    text: str = Field(...)


class GetMeResponse(Response):
    result: Optional[User] = Field(None)


class GetWebhookInfoResponse(Response):
    result: Optional[WebhookInfo] = Field(None)


class SetWebhookResponse(Response):
    result: bool = Field(False)


class SendMessageResponse(Response):
    result: Optional[Message] = Field(None)

