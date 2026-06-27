# Prime

Prime Code Agent Runtime MVP is a local CLI-first fake agent runtime prototype.

## Run From This Checkout

```powershell
.\.venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"
prime
```

Exit the REPL with:

```text
/exit
```

## Install `prime` For Any Folder

From this repository root, run:

```powershell
.\scripts\install-prime.ps1 -UpdateUserPath
```

Open a new terminal, move to any project folder, then run:

```powershell
prime
```

The displayed `workspace` is the folder where you launched `prime`.

MVP note: the current runtime does not read or modify real project files yet.
