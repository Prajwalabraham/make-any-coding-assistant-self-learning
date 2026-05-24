# Vendored from Anthropic Skills

This directory is a verbatim copy of `skills/skill-creator/` from
https://github.com/anthropics/skills, licensed under Apache License
2.0 (see `LICENSE.txt`).

Upstream commit at vendoring: **690f15cac7f7b4c055c5ab109c79ed9259934081**
(2026-05, "Add CMA claude-api skill updates").

It is bundled here so the `skill-distiller` workflow can hand off to
the official skill-authoring expertise instead of reimplementing it.

To update: re-vendor from the upstream repo wholesale. Do not modify
in place; any patches or workflow integrations belong in
`skill-distiller/SKILL.md` as a thin wrapper.
