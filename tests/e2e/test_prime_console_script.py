import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_prime_console_script_uses_launch_directory_as_workspace(tmp_path) -> None:
    executable = Path(sys.executable)
    prime_name = "prime.exe" if os.name == "nt" else "prime"
    prime_executable = executable.parent / prime_name
    if not prime_executable.exists():
        pytest.skip("prime console script is not installed in this Python environment")

    result = subprocess.run(
        [str(prime_executable)],
        cwd=tmp_path,
        input="/exit\n",
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )

    assert result.returncode == 0
    assert "Prime Code Agent" in result.stdout
    assert f"workspace: {tmp_path}" in result.stdout
