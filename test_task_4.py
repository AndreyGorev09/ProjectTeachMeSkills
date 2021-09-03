from random import randint

import httpx
import pytest

from asgi import app


@pytest.mark.asyncio
async def test():
    url = "/task/4"

    a, b = [randint(1, 100) for _ in "ab"]

    async with httpx.AsyncClient(app=app, base_url="http://asgi") as client:
        resp: httpx.Response = await client.post(url, json=a)
        assert resp.status_code == 200
        assert resp.json() == {"data": {"n": a}}

        resp = await client.post(url, json=b)
        assert resp.status_code == 200
        assert resp.json() == {"data": {"n": a + b}}

        resp = await client.post(url, json="stop")
        assert resp.status_code == 200
        assert resp.json() == {"data": {"n": a + b}}