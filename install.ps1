# Bootstrap for the self-learning-agent installer (Windows / PowerShell).
#
# Usage:
#   iwr -useb https://raw.githubusercontent.com/Prajwalabraham/make-any-coding-assistant-self-learning/main/install.ps1 | iex
#
# Mirrors install.sh: download tarball, drop into a cache dir, link the
# sla runner onto PATH, hand off to `sla init`.

$ErrorActionPreference = 'Stop'

$Repo     = if ($env:SLA_REPO) { $env:SLA_REPO } else { 'Prajwalabraham/make-any-coding-assistant-self-learning' }
$Ref      = if ($env:SLA_REF)  { $env:SLA_REF }  else { 'main' }
$CacheDir = Join-Path $env:LOCALAPPDATA 'self-learning-agent'
$BinDir   = Join-Path $env:LOCALAPPDATA 'self-learning-agent\bin'

function Say($tag, $msg) { Write-Host "  $tag $msg" -ForegroundColor Cyan }

Say '==>' "Fetching $Repo@$Ref"
$tmp = New-TemporaryFile
Remove-Item $tmp
$tmp = New-Item -ItemType Directory -Path "$($tmp.FullName)_dir"

try {
    $archive = Join-Path $tmp 'src.zip'
    Invoke-WebRequest -UseBasicParsing `
        -Uri "https://codeload.github.com/$Repo/zip/$Ref" `
        -OutFile $archive
    Expand-Archive -Path $archive -DestinationPath $tmp -Force

    $src = Get-ChildItem -Path $tmp -Directory | Where-Object { $_.Name -like "*-$Ref" } | Select-Object -First 1
    if (-not $src) { throw "extracted archive missing expected directory" }

    New-Item -ItemType Directory -Force -Path $CacheDir, $BinDir | Out-Null
    if (Test-Path "$CacheDir\sla") { Remove-Item -Recurse -Force "$CacheDir\sla" }
    Copy-Item -Recurse "$($src.FullName)\sla" "$CacheDir\sla"

    $shim = @"
@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "$CacheDir\sla\sla.ps1" %*
"@
    Set-Content -Path "$BinDir\sla.cmd" -Value $shim -Encoding ASCII
    Say '==>' "Installed sla -> $BinDir\sla.cmd"

    if (($env:Path -split ';') -notcontains $BinDir) {
        Say 'note' "Add $BinDir to PATH to use 'sla' directly."
    }

    & pwsh -NoProfile -ExecutionPolicy Bypass -File "$CacheDir\sla\sla.ps1" init
}
finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
