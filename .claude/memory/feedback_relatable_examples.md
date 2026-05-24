---
name: relatable-examples
description: Use examples the broad developer audience can relate to, not personal-setup quirks
metadata:
  type: feedback
---

When writing for a developer audience, pick examples that 80% of devs have hit personally. Avoid pulling examples straight from one user's machine state (their cloud provider, their game install, their team's specific quarterly incident).

**Why:** First draft of the README used "uses Azure Foundry at this endpoint" and "Steam at C:\Program Files (x86)\Steam, permitted to clean CS2 crash dumps" as canonical memory examples. These are real Hermes entries on this user's machine but almost no reader will recognize them. Same problem with the "no DB mocks because of a Q3 prod migration" feedback example, too narrow and incident-specific.

**How to apply:** For memory examples, prefer things like "use pnpm not npm in this repo", "this project uses conventional commits", "deploys go through GitHub Actions on merge to main". For feedback examples, prefer "always run the tests before suggesting a fix", "research the codebase before proposing a plan", "never force-push to shared branches". Universal pain points, not personal anecdotes.
