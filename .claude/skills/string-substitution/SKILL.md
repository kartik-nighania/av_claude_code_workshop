---
description: used to print and check how string substitution works
arguments: org-name username
---

Log the following to logs/${CLAUDE_SESSION_ID}.log
and also return it back to the model:

```

# the ARGUMENTS

$ARGUMENTS

# Second argument

$ARGUMENTS[1]

# Named argument org-name

$org-name

# Directory of Skill

${CLAUDE_SKILL_DIR}

```
