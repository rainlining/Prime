param(
    [switch]$UpdateUserPath
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$binDir = Join-Path $env:USERPROFILE ".local\bin"
$cmdPath = Join-Path $binDir "prime.cmd"
$staleExePath = Join-Path $binDir "prime.exe"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Install uv first, then re-run this script."
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    Push-Location $projectRoot
    try {
        uv venv --python 3.11 .venv
        if ($LASTEXITCODE -ne 0) {
            throw "uv venv failed with exit code $LASTEXITCODE."
        }
    } finally {
        Pop-Location
    }
}

uv pip install --python $venvPython --editable $projectRoot
if ($LASTEXITCODE -ne 0) {
    throw "uv pip install failed with exit code $LASTEXITCODE."
}

New-Item -ItemType Directory -Force -Path $binDir | Out-Null

if (Test-Path -LiteralPath $staleExePath) {
    Remove-Item -LiteralPath $staleExePath -Force
    Write-Host "Removed stale shim: $staleExePath"
}

$userProfile = [Environment]::GetFolderPath("UserProfile")
$cmdProjectRoot = $projectRoot
$cmdPython = $venvPython
if ($projectRoot.StartsWith($userProfile, [System.StringComparison]::OrdinalIgnoreCase)) {
    $cmdProjectRoot = "%USERPROFILE%" + $projectRoot.Substring($userProfile.Length)
}
if ($venvPython.StartsWith($userProfile, [System.StringComparison]::OrdinalIgnoreCase)) {
    $cmdPython = "%USERPROFILE%" + $venvPython.Substring($userProfile.Length)
}

$cmdContent = @"
@echo off
set "PRIME_PROJECT_ROOT=$cmdProjectRoot"
"$cmdPython" -m prime.cli.main %*
"@

$cmdContent = $cmdContent.Replace("`r`n", "`n").Replace("`r", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($cmdPath, $cmdContent, [System.Text.Encoding]::ASCII)

if ($UpdateUserPath) {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $entries = @()
    if ($userPath) {
        $entries = $userPath -split ";" | Where-Object { $_ }
    }

    if ($entries -notcontains $binDir) {
        $newUserPath = (@($entries) + $binDir) -join ";"
        [Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
        Write-Host "Added to user PATH: $binDir"
    } else {
        Write-Host "User PATH already contains: $binDir"
    }

    if (($env:Path -split ";") -notcontains $binDir) {
        $env:Path = "$binDir;$env:Path"
    }
} else {
    Write-Host "prime installed. Add this directory to PATH if needed: $binDir"
}

Write-Host "Installed prime shim: $cmdPath"
Write-Host "Prime source: $projectRoot"
Write-Host "Open a new terminal and run: prime"
