from io import StringIO

from rich.console import Console

from prime.cli.main import run_repl


def test_repl_exits_on_exit_command(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    output = StringIO()
    console = Console(file=output, force_terminal=False, width=120)
    inputs = iter(["/exit"])

    run_repl(console=console, input_func=lambda prompt: next(inputs))

    rendered = output.getvalue()
    assert "Prime Code Agent" in rendered
    assert f"workspace: {tmp_path}" in rendered
    assert "Task accepted" not in rendered


def test_repl_routes_regular_input_to_task_placeholder() -> None:
    output = StringIO()
    console = Console(file=output, force_terminal=False, width=120)
    inputs = iter(["do something fake", "/exit"])

    run_repl(console=console, input_func=lambda prompt: next(inputs))

    assert "Task accepted. Runtime loop is not implemented yet." in output.getvalue()
