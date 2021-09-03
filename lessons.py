from typing import Optional


def task_3(name: Optional[str] = None):
    name = name or "👺"
    return f"Hello, [{name}]!"