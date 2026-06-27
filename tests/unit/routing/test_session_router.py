from prime.routing.session_router import RouteType, SessionRouter


def test_exit_command_routes_to_exit() -> None:
    result = SessionRouter().route("/exit")

    assert result.route_type == RouteType.EXIT
    assert result.command == "/exit"
    assert result.payload == ""


def test_whitespace_wrapped_exit_command_routes_to_exit() -> None:
    result = SessionRouter().route("  /exit  ")

    assert result.route_type == RouteType.EXIT


def test_regular_input_routes_to_task() -> None:
    raw_input = "please inspect this fake task"

    result = SessionRouter().route(raw_input)

    assert result.route_type == RouteType.TASK
    assert result.command is None
    assert result.payload == raw_input
