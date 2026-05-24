# Third-Party Attribution

## Anthropic Skills — `skill-creator`

This repository vendors the `skill-creator` skill from
https://github.com/anthropics/skills, licensed under the Apache License,
Version 2.0.

Copies live at:

- `sla/templates/claude-code/.claude/skills/skill-creator/`
- `sla/templates/codex/.agents/skills/skill-creator/`
- `sla/templates/aider/.aider/skills/skill-creator/`

Each vendored copy retains its upstream `LICENSE.txt` and a
`VENDORED.md` recording the upstream commit hash. The wrapper skill
`skill-distiller` (MIT, in each template) delegates skill authoring
to `skill-creator` rather than reimplementing it.

Cursor's template does not vendor `skill-creator` because Cursor uses
`.mdc` rules instead of `SKILL.md` files; the upstream scripts are
not directly compatible. The Cursor `skill-distiller` rule cites the
upstream methodology by URL instead.

You may obtain a copy of the Apache License, Version 2.0 at:
http://www.apache.org/licenses/LICENSE-2.0
