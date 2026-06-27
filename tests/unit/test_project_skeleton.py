from pathlib import Path

import prime


def test_prime_package_importable() -> None:
    assert prime.__version__ == "0.1.0"


def test_expected_project_skeleton_exists() -> None:
    root = Path(__file__).resolve().parents[2]

    assert (root / "pyproject.toml").is_file()
    assert (root / "config" / "settings.yaml").is_file()
    assert (root / "src" / "prime" / "__init__.py").is_file()
    assert (root / "tests" / "unit").is_dir()
    assert (root / "tests" / "integration").is_dir()
    assert (root / "tests" / "e2e").is_dir()
