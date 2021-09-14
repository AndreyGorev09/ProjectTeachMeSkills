import json
import traceback
from random import choice
from string import ascii_lowercase
from typing import Optional
from typing import Tuple
from typing import Union

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ipware import get_client_ip

from .models import Check
from .models import CheckT
from .models import Numbers


def get_user_name(request: HttpRequest) -> Optional[str]:
    if (
        not hasattr(request, "session")
        or not request.session
        or not (name := request.session.get("name"))
    ):
        return None

    return name


def create_new_user_name() -> str:
    def word() -> str:
        return "".join(choice(ascii_lowercase) for _ in range(6))

    return "-".join(word() for _ in "123")


def set_user_name(request: HttpRequest, name: str) -> None:
    if not hasattr(request, "session"):
        return

    request.session["name"] = name


def add_number(name: str, number: int):
    obj: Tuple[Numbers, bool] = Numbers.objects.get_or_create(name=name)
    rec, _created = obj
    rec.n += number
    rec.save()
    return rec.n


def validate_number(number: int) -> None:
    lower_bound, upper_bound = -100, 100
    if not (lower_bound <= number <= upper_bound):
        raise ValueError(
            f"number {number} is not in range {(lower_bound, upper_bound)}"
        )


def parse_payload(request: HttpRequest) -> Union[str, int, None]:
    if not request.body:
        raise ValueError("non-empty body is required")

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError as err:
        raise ValueError(f"malformed payload: {request.body!r} ({err})") from err

    if isinstance(payload, int):
        validate_number(payload)
    elif payload != "stop":
        raise ValueError(
            f"value {payload!r} is not acceptable: MUST be either int, or 'stop'"
        )

    return payload


class UnprocessableEntityResponse(JsonResponse):
    status_code = 422


@csrf_exempt
@require_http_methods(["POST"])
def task(request: HttpRequest) -> HttpResponse:
    name = get_user_name(request) or create_new_user_name()
    set_user_name(request, name)

    try:
        payload = parse_payload(request)
    except ValueError as err:
        return UnprocessableEntityResponse(str(err), safe=False)

    if isinstance(payload, int):
        current = add_number(name, payload)
    elif payload == "stop":
        current = add_number(name, 0)
    else:
        current = None

    return JsonResponse(
        current,
        safe=False,
        headers={
            "Access-Control-Allow-Headers": "Origin, Content-Type, X-Auth-Token",
            "Access-Control-Allow-Methods": "GET, POST, PATCH, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Origin": "*",
        },
    )


@csrf_exempt
def check(request: HttpRequest) -> HttpResponse:
    resp_payload = {"ok": False}

    try:
        ip, _routable = get_client_ip(request)

        obj: CheckT = CheckT.parse_raw(request.body)
        obj.ip = ip

        dbobj = Check(**obj.dict())
        dbobj.save()

        obj = CheckT.from_orm(dbobj)
        resp_payload.update(
            {
                "ok": True,
                "data": obj.dict(),
            }
        )

    except Exception as err:
        resp_payload["description"] = str(err)
        resp_payload["tb"] = traceback.format_exc()

    return JsonResponse(resp_payload, status=200 if resp_payload["ok"] else 500)


@csrf_exempt
def index(request: HttpRequest) -> HttpResponse:
    if request.method.upper() == "GET":
        return render(request, "task4/index.html")
    return check(request)