import tomllib
from pathlib import Path

from typer.testing import CliRunner

from prime.cli.main import app


def test_prime_cli_displays_product_name_and_workspace(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, [])

    assert result.exit_code == 0
    assert "Prime Code Agent" in result.output
    assert f"workspace: {tmp_path}" in result.output


def test_prime_console_script_declared() -> None:
    root = Path(__file__).resolve().parents[3]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["scripts"]["prime"] == "prime.cli.main:main"
