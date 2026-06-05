# sla.ps1: the PowerShell sibling of `sla`.
#
# Same flow: pick agent, pick scope, copy templates with overwrite
# prompts. Pure PowerShell so it works on stock Windows without WSL
# or a bash runtime.

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('init', 'list', 'help')]
    [string]$Subcommand = 'init'
)

$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$TemplateRoot = Join-Path $Here 'templates'

function Say($tag, $msg) { Write-Host "  $tag $msg" -ForegroundColor Cyan }
function Ok($msg)        { Write-Host "  + $msg" -ForegroundColor Green }
function Warn($msg)      { Write-Host "  ! $msg" -ForegroundColor Yellow }
function Fail($msg)      { Write-Host "  error $msg" -ForegroundColor Red; exit 1 }

function Ask-Choice($Prompt, [string[]]$Options) {
    Write-Host "`n  $Prompt"
    for ($i = 0; $i -lt $Options.Count; $i++) {
        Write-Host ("    {0}) {1}" -f ($i + 1), $Options[$i])
    }
    while ($true) {
        $raw = Read-Host '  >'
        if ($raw -match '^\d+$') {
            $n = [int]$raw
            if ($n -ge 1 -and $n -le $Options.Count) { return $Options[$n - 1] }
        }
        Warn 'invalid choice, try again'
    }
}

function Ask-YesNo($Prompt, $Default = 'n') {
    $hint = if ($Default -eq 'y') { '[Y/n]' } else { '[y/N]' }
    $raw = Read-Host "`n  $Prompt $hint"
    if (-not $raw) { $raw = $Default }
    return $raw -match '^[Yy]'
}

function Resolve-Target($Agent) {
    $scope = Ask-Choice 'Install scope?' @('this project (cwd)', 'global (your home config)')
    switch ("$Agent`:$scope") {
        'claude-code:this project (cwd)'        { return (Get-Location).Path }
        'claude-code:global (your home config)' { return (Join-Path $HOME '.claude') }
        'codex:this project (cwd)'              { return (Get-Location).Path }
        'codex:global (your home config)'       { return (Join-Path $HOME '.codex') }
        'cursor:this project (cwd)'             { return (Get-Location).Path }
        'cursor:global (your home config)'      { return (Join-Path $HOME '.cursor') }
        'aider:this project (cwd)'              { return (Get-Location).Path }
        'aider:global (your home config)'       { return $HOME }
        default { Fail "unknown agent/scope combo: $Agent / $scope" }
    }
}

function Copy-Template($Src, $Dst) {
    if (-not (Test-Path $Src)) { Fail "template directory missing: $Src" }
    if (-not (Test-Path $Dst)) { New-Item -ItemType Directory -Force -Path $Dst | Out-Null }

    Get-ChildItem -Path $Src -Recurse -File -Force | ForEach-Object {
        $rel = $_.FullName.Substring($Src.Length).TrimStart('\','/')
        $target = Join-Path $Dst $rel
        if (Test-Path $target) {
            Warn "exists: $target"
            if (-not (Ask-YesNo '  overwrite?')) {
                Say 'skip' $rel
                return
            }
        }
        $parent = Split-Path -Parent $target
        if ($parent -and -not (Test-Path $parent)) {
            New-Item -ItemType Directory -Force -Path $parent | Out-Null
        }
        Copy-Item -LiteralPath $_.FullName -Destination $target -Force
        Ok "wrote $rel"
    }
}

function Set-PythonInterpreter($Dst) {
    # The Claude Code hooks and the memory-init skill invoke Python 3. The
    # template ships `python3`, but on Windows that name is often absent
    # (python.org installs expose `python` and the `py` launcher). Pick the
    # interpreter that actually exists and rewrite the copied files so the
    # hooks don't fail with "python3: command not found".
    $interp = $null
    foreach ($cand in @('python', 'py', 'python3')) {
        if (Get-Command $cand -ErrorAction SilentlyContinue) { $interp = $cand; break }
    }
    if (-not $interp) { Warn 'no Python interpreter on PATH; hooks need Python 3.'; return }
    if ($interp -eq 'python3') { return }
    $files = @(
        (Join-Path $Dst '.claude\settings.json'),
        (Join-Path $Dst '.claude\skills\memory-init\SKILL.md')
    )
    foreach ($f in $files) {
        if (Test-Path -LiteralPath $f) {
            $content = (Get-Content -LiteralPath $f -Raw) -replace 'python3 ', "$interp "
            Set-Content -LiteralPath $f -Value $content -NoNewline
        }
    }
    Ok "wired Python hooks to '$interp' (python3 not found)"
}

function Cmd-Init {
    Write-Host "`n  sla init  self-learning scaffold for coding agents" -ForegroundColor Magenta

    $agentLabel = Ask-Choice 'Which coding agent?' @('Claude Code','Codex CLI','Cursor','Aider')
    $agent = switch ($agentLabel) {
        'Claude Code' { 'claude-code' }
        'Codex CLI'   { 'codex' }
        'Cursor'      { 'cursor' }
        'Aider'       { 'aider' }
    }

    $target = Resolve-Target $agent
    Say '==>' "installing $agent into $target"

    if (-not (Ask-YesNo 'Proceed?' 'y')) { Fail 'aborted by user' }

    Copy-Template (Join-Path $TemplateRoot $agent) $target
    if ($agent -eq 'claude-code') { Set-PythonInterpreter $target }

    Write-Host "`n  + self-learning agent installed.`n" -ForegroundColor Green
    switch ($agent) {
        'claude-code' {
            Write-Host "  next: open the project in Claude Code. The SessionStart hook"
            Write-Host "        bootstraps the agent on first turn. Schedule the keeper"
            Write-Host "        with: /schedule create memory-keeper-weekly '0 9 * * 1'"
        }
        'codex' {
            Write-Host "  next: run 'codex' in the project. AGENTS.md is auto-loaded."
            Write-Host "        Wire the keeper to Task Scheduler (see AGENTS.md)."
        }
        'cursor' {
            Write-Host "  next: open the project in Cursor. .cursor/rules/*.mdc are"
            Write-Host "        auto-applied. Schedule the keeper via Cursor Background"
            Write-Host "        Agents (weekly, 0 9 * * 1)."
        }
        'aider' {
            Write-Host "  next: cd into the project and run 'aider'. CONVENTIONS.md and"
            Write-Host "        the memory index auto-load via .aider.conf.yml. Wire the"
            Write-Host "        keeper to Task Scheduler (see CONVENTIONS.md)."
        }
    }
    Write-Host ''
}

function Cmd-List {
    Write-Host 'available templates:'
    Get-ChildItem -Path $TemplateRoot -Directory | ForEach-Object {
        Write-Host "  - $($_.Name)"
    }
}

function Cmd-Help {
    @"
sla: self-learning-agent scaffolder

usage:
  sla init      interactive: pick agent, pick scope, drop the scaffold
  sla list      show available agent templates
  sla help      this message
"@
}

switch ($Subcommand) {
    'init' { Cmd-Init }
    'list' { Cmd-List }
    'help' { Cmd-Help }
}
