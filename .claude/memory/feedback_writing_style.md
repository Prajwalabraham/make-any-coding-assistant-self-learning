---
name: writing-style
description: Style rules for prose and code comments in this user's content
metadata:
  type: feedback
---

Two hard rules:

1. **Code comments / docstrings explain WHY, not WHAT.** The code already shows what it does; a comment that paraphrases the code is noise. Reserve comments for intent, constraints, or non-obvious reasoning.
2. **Prose for articles avoids em dashes.** They read as AI-generated. Use periods, commas, parentheses, or sentence restructuring instead. Same for excessive "—" or "→" decorations.

**Why:** User flagged both in a review of the self-learning-agent README and the hook scripts. The em dashes specifically made the article feel machine-written.
**How to apply:** Every Medium article, README, or blog post intended for humans. Every Python/TS docstring and inline comment. Does not apply to literal command output or quoted Hermes content.
