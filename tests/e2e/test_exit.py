import subprocess
import sys


def test_prime_module_exits_on_exit_command() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "prime.cli.main"],
        input="/exit\n",
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )

    assert result.returncode == 0
    assert "Prime Code Agent" in result.stdout
    assert "workspace:" in result.stdout
