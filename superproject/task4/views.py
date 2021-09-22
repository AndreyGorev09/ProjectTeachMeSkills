from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView

from task4.models import Numbers

import json


def hw(request: HttpRequest):
    return HttpResponse("Hello world")


class ShowNumbersView(ListView):
    templates_name = "task4/numbers_list.html"
    model = Numbers


def view(request: HttpRequest):
    if request.method != "POST":
        return HttpResponse(""""Use only the"POST" method""", status=405)

    name = request.headers.get("x-user")
    if not name: return HttpResponse("Header X-USER is not set", status=403)
    try:
        cell = json.loads(request.body)
        obj, _created = Numbers.objects.get_or_create(name=name)
        if type(cell) is int:
            if not -100 <= cell <= 100:
                return HttpResponse("Enter a number from -100 to 100", status=422)
            obj.n += cell
            obj.save()
            return HttpResponse({obj.n})
        elif cell != 'stop':
            return HttpResponse("This input is not supported", status=422)
        return HttpResponse({obj.n})
    except ValueError as err:
        return HttpResponse(f"""Your "body" should be a "number" or the word "stop": {err} """, status=422)









