from pathlib import Path


def test_install_prime_script_declares_uv_tool_install() -> None:
    root = Path(__file__).resolve().parents[3]
    script = (root / "scripts" / "install-prime.ps1").read_text(encoding="utf-8")

    assert "prime.cmd" in script
    assert "-m prime.cli.main" in script
    assert "PRIME_PROJECT_ROOT" in script
    assert "%USERPROFILE%" in script
    assert "Encoding]::ASCII" in script
    assert "uv pip install --python $venvPython --editable $projectRoot" in script
    assert "UpdateUserPath" in script


def test_readme_documents_global_prime_install() -> None:
    root = Path(__file__).resolve().parents[3]
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert ".\\scripts\\install-prime.ps1 -UpdateUserPath" in readme
    assert "The displayed `workspace` is the folder where you launched `prime`." in readme
