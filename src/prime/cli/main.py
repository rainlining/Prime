from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from prime import __version__
from prime.routing.session_router import RouteType, SessionRouter

app = typer.Typer(add_completion=False, help="Prime Code Agent CLI.")


def render_startup(console: Console | None = None, workspace: Path | None = None) -> None:
    target_console = console or Console()
    current_workspace = workspace or Path.cwd()

    target_console.print("Prime Code Agent", soft_wrap=True)
    target_console.print(f"workspace: {current_workspace}", soft_wrap=True)
    target_console.print()


def run_repl(
    console: Console | None = None,
    router: SessionRouter | None = None,
    input_func=input,
) -> None:
    target_console = console or Console()
    session_router = router or SessionRouter()

    render_startup(console=target_console)

    while True:
        try:
            raw_input = input_func("> ")
        except EOFError:
            break

        route = session_router.route(raw_input)
        if route.route_type == RouteType.EXIT:
            break
        if route.route_type == RouteType.TASK:
            target_console.print("Task accepted. Runtime loop is not implemented yet.", soft_wrap=True)


@app.callback(invoke_without_command=True)
def cli(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", help="Show the installed Prime version."),
    ] = False,
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        run_repl()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
