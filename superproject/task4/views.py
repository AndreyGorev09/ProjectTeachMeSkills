from django.http import HttpRequest, HttpResponse

from task4.models import Numbers

import json




def hello_world(request: HttpRequest):
    return HttpResponse("Hello world")


def view(request: HttpRequest):
    if request.method != "POST":
        return HttpResponse(status=405)

    name = request.headers.get("x-user")
    if not name: return HttpResponse(status=422)

    cell = json.loads(request.body)
    obj,_created = Numbers.objects.get_or_create(name=name)
    if type(cell) is int:
        obj.n += cell
        obj.save()
        return HttpResponse(f"Hello {name}, your number = {obj.n}")
    elif cell == 'stop':
        return HttpResponse(f"Your body '{cell}', actual numbers {obj.n}")
    else:
        return HttpResponse("""Your "body" should be a "number" or the word "stop" """)









