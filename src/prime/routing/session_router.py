from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RouteType(StrEnum):
    EXIT = "exit"
    TASK = "task"


@dataclass(frozen=True)
class RouteResult:
    route_type: RouteType
    command: str | None
    payload: str


class SessionRouter:
    def route(self, raw_input: str) -> RouteResult:
        payload = raw_input.strip()

        if payload == "/exit":
            return RouteResult(route_type=RouteType.EXIT, command="/exit", payload="")

        return RouteResult(route_type=RouteType.TASK, command=None, payload=raw_input)
