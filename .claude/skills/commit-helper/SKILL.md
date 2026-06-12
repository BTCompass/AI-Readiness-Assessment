---
name: commit-helper
description: Analyze staged git changes and generate a clear, well-formatted commit message
---

## Steps

1. Run `git diff --staged` to see all staged changes.
2. Run `git status` to see which files are staged.
3. Analyze what changed: what files, what kind of change (new feature, bug fix, refactor, docs, config, test, etc.), and why it likely happened based on context.
4. Write a commit message following this format:

```
<type>(<scope>): <short summary>

<optional body explaining what and why, not how>
```

### Types
- `feat` — new feature
- `fix` — bug fix
- `refactor` — code restructure without behavior change
- `docs` — documentation only
- `test` — adding or fixing tests
- `chore` — tooling, config, deps, CI
- `style` — formatting, whitespace, no logic change
- `perf` — performance improvement

### Rules
- Summary line: max 72 characters, imperative mood ("add X", not "added X")
- Scope is optional but use it when the change is clearly scoped to one module, file, or feature area
- Body: explain *why*, not *what* (the diff already shows what). Wrap at 72 chars.
- If there are no staged changes, say so and remind the user to stage files with `git add`.

5. Present the message to the user and ask if they want to commit with it, edit it, or cancel.
6. If confirmed, run `git commit -m "<message>"` using a heredoc to preserve formatting.
