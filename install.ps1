# Kept as a one-shot copy (no symlink, no submodule) so each target
# project owns its memory store and skills independently. Sharing the
# same .claude/ across repos would cross-contaminate learned context.

param(
    [Parameter(Mandatory = $true)]
    [string]$Target,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot ".claude"
$dest = Join-Path (Resolve-Path $Target) ".claude"

if (Test-Path $dest) {
    if (-not $Force) {
        Write-Host "$dest already exists. Re-run with -Force to overwrite." -ForegroundColor Yellow
        exit 1
    }
    Remove-Item -Recurse -Force $dest
}

Copy-Item -Recurse $source $dest
Write-Host "Installed self-learning .claude/ into $dest" -ForegroundColor Green
Write-Host "Next: open the project in Claude Code. The SessionStart hook will bootstrap."
