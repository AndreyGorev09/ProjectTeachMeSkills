import hmac
import mimetypes
import traceback
from functools import wraps
from pathlib import Path
from typing import Type

from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.responses import Response

from config import settings


def apply_cache_headers(response: Response) -> None:
    cache_params = (
        "immutable",
        "public",
        f"max_age={60 * 60}",
    )

    response.headers["Cache-Control"] = ",".join(cache_params)


def static_response(file_name: str) -> Response:
    def get_file_path_safe() -> Path:
        file_path = Path(file_name).resolve()
        if not file_path.is_file():
            raise HTTPException(
                detail=f"file {file_name!r} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return file_path

    def calc_media_type() -> str:
        return mimetypes.guess_type(file_name)[0] or "text/plain"

    file_path = get_file_path_safe()
    media_type = calc_media_type()

    with file_path.open("rb") as stream:
        content = stream.read()
        return Response(content=content, media_type=media_type)


def authorize(token: str) -> None:
    exc = HTTPException(status_code=404, detail="not found")

    if not settings.admin_token:
        raise exc

    tokens_are_equal = hmac.compare_digest(token, settings.admin_token)
    if not tokens_are_equal:
        raise exc


BaseModelType = Type[BaseModel]


def update_forward_refs(klass: BaseModelType) -> BaseModelType:
    klass.update_forward_refs()
    return klass


def hide_webhook_secret(whi) -> None:
    if not (whi and whi.url):
        return

    whi.url = whi.url.replace(settings.webhook_secret, "***")


def safe(handler):
    @wraps(handler)
    async def safe_handler(*args, **kwargs):
        try:
            return await handler(*args, **kwargs)
        except Exception:
            traceback.print_exc()

    return safe_handler