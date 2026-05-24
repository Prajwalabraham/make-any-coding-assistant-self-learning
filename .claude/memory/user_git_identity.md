---
name: user-git-identity
description: Correct git author identity to use for commits in this user's personal repos
metadata:
  type: user
---

For personal repos, commits must be authored as `Prajwal Abraham <prajwalabaraham.21@gmail.com>` — not the `prajwal@auralis.ai` work email and not the bare `prajwal` name from the global git config.

**Why:** The user corrected an initial commit that used `vinay@askzuro.com` (wrong) and then `prajwal@auralis.ai` (also wrong). Personal GitHub account is `Prajwalabraham`; gmail address links commits to that profile.
**How to apply:** When committing to anything under the user's personal GitHub (`Prajwalabraham`), pass `-c user.name="Prajwal Abraham" -c user.email="prajwalabaraham.21@gmail.com"` or use `--reset-author` after setting those values. Work repos (Zuro / askzuro.com) may want a different identity — confirm before assuming.
