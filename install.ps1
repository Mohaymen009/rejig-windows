# Rejig for Windows installer.
# Installs the engine into %USERPROFILE%\Rejig, applies the patches, installs the launcher,
# and puts a "Rejig" shortcut on the Desktop.
#
#   powershell -ExecutionPolicy Bypass -File install.ps1 [-RegisterMcp]
#
# -RegisterMcp also adds the MCP server to Claude Code (needs the `claude` command).
param([switch]$RegisterMcp)

$ErrorActionPreference = 'Stop'
$project = $PSScriptRoot
$runtime = Join-Path $env:USERPROFILE 'Rejig'
$venv = Join-Path $runtime '.venv'
$py = Join-Path $venv 'Scripts\python.exe'

# Python 3.12 or newer (the lock files support 3.12+).
$launcher = $null
foreach ($v in '3.13', '3.12', '3.14') {
    $ErrorActionPreference = 'Continue'
    & py "-$v" -c "import sys" 2>$null
    $ok = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = 'Stop'
    if ($ok) { $launcher = "-$v"; break }
}
if (-not $launcher) { throw 'Python 3.12 or newer is required: https://www.python.org/downloads/windows/ (tick "py launcher").' }

# Git for Windows provides git (to fetch the engine) and patch.exe.
$patchExe = @('C:\Program Files\Git\usr\bin\patch.exe', 'C:\Program Files (x86)\Git\usr\bin\patch.exe') |
    Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $patchExe) { throw 'Git for Windows is required: https://git-scm.com/download/win' }

New-Item -ItemType Directory -Force $runtime | Out-Null
if (-not (Test-Path $py)) { & py $launcher -m venv $venv; if ($LASTEXITCODE) { throw 'Creating the virtual environment failed.' } }

& $py -m pip install --require-hashes -r "$project\requirements.lock" -r "$project\requirements-mcp.lock"
if ($LASTEXITCODE) { throw 'Installing dependencies failed.' }
# --force-reinstall: start from the unpatched engine every run so the patches always apply cleanly.
& $py -m pip install --no-deps --force-reinstall -r "$project\requirements.txt"
if ($LASTEXITCODE) { throw 'Installing the engine failed.' }

$engine = & $py -c "import pathlib, ios_homescreen; print(pathlib.Path(ios_homescreen.__file__).parent.parent)"
# git's autocrlf may have written the engine's files with CRLF; normalise to LF so the patches apply.
& $py "$project\launcher\normalize_eol.py" $engine
foreach ($p in Get-ChildItem "$project\patches\*.patch" | Sort-Object Name) {
    $bytes = [IO.File]::ReadAllBytes($p.FullName)
    $text = [Text.Encoding]::UTF8.GetString($bytes) -replace "`r`n", "`n"
    $tmp = Join-Path $env:TEMP ("rejig-" + $p.Name)
    [IO.File]::WriteAllBytes($tmp, [Text.UTF8Encoding]::new($false).GetBytes($text))
    Write-Host "Applying $($p.Name)"
    & $patchExe --batch --forward --binary --no-backup-if-mismatch -p1 -d $engine -i $tmp
    if ($LASTEXITCODE) { throw "Patch $($p.Name) failed." }
    Remove-Item $tmp
}

# The MCP companion runs in the same runtime; replace any older copy.
Remove-Item -Recurse -Force "$engine\rejig_mcp" -ErrorAction SilentlyContinue
Copy-Item "$project\rejig_mcp" "$engine\rejig_mcp" -Recurse -Force
Get-ChildItem "$engine\rejig_mcp" -Recurse -Directory -Filter __pycache__ -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Copy-Item "$project\launcher\approve.py" "$runtime\approve.py" -Force
Copy-Item "$project\launcher\rejig.py" "$runtime\rejig.py" -Force
Copy-Item "$project\launcher\Rejig.cmd" "$runtime\Rejig.cmd" -Force

# Desktop shortcut.
try {
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Rejig.lnk'))
    $lnk.TargetPath = Join-Path $runtime 'Rejig.cmd'
    $lnk.WorkingDirectory = $runtime
    $lnk.Description = 'Rearrange your iPhone Home Screen'
    $lnk.Save()
} catch { Write-Host "Could not create the Desktop shortcut: $_" }

if ($RegisterMcp) {
    & claude mcp add --scope user rejig -- $py -m rejig_mcp
}

Write-Host ''
Write-Host 'Installed.'
Write-Host "  Try it without a phone:  $runtime\Rejig.cmd --demo"
Write-Host "  With your iPhone (USB):  $runtime\Rejig.cmd"
Write-Host "  MCP server command:      $py -m rejig_mcp"
