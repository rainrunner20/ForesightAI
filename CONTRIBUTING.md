# Team development workflow

Keep `main` reviewable. One feature branch = one coherent change with its own tests and documentation. Feature branches should be retained after a merge unless the team explicitly decides otherwise.

## Before starting

```powershell
git status --short --branch
git remote -v
git switch main
git pull --ff-only
git status --short --branch
git switch -c feature/short-description
```

Verify you're in the intended repository and the working tree is clean before changes. In VS Code, make small commits as you implement and test real work.

## Commit naming

Use concise Conventional Commit subjects where they clarify intent:

- `feat(data): support AVeriTeC JSONL files`
- `test(metrics): cover incorrect evidence references`
- `fix(ui): preserve slider interaction on rerender`
- `docs(research): define token-matched control`

Write natural comments only when code behavior or tradeoffs are not obvious. Avoid narrating every line. Never falsify timestamps, commits, tests, authorship, or experiments.

## Pull request checklist

- [ ] Scope and motivation explained
- [ ] Automated checks pass locally
- [ ] No datasets, secrets, or output artifacts accidentally committed
- [ ] UI numbers labeled synthetic unless backed by a named experiment
- [ ] Results document model, dataset split, prompt version, and decoding parameters
- [ ] Limitations and next steps described

## Review and merge

Open a PR targeting `main`, ask at least one teammate to review, and apply specific feedback. Squash merge for a clean main history if appropriate, while preserving the source branch. Do not merge broken builds simply to increase commit count.

## Academic integrity and datasets

A real experiment must be reproducible and clearly distinguish measured data from illustrative examples. Attribute original datasets and prior research, obey licensing terms, and do not claim an unimplemented feature exists.
