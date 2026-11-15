# Publish this local Git repository to GitHub

The archive already contains a local Git history and three preserved feature branches. It was built with an honest setup identity (`ForesightAI Setup <setup@localhost>`); these are actual local commits made while assembling the scaffold. No GitHub pull requests are claimed to exist.

## Step 1 — create an empty GitHub repository

Sign into [github.com/new](https://github.com/new) as **rainrunner20**. Name the repository `ForesightAI`. Choose public/private based on the team's preference. **Do not** initialize it with a README, `.gitignore`, or license because those already exist locally.

## Step 2 — unzip, inspect, and push

Open the extracted `foresight-ai` folder in VS Code. In its PowerShell terminal:

```powershell
git status --short --branch
git log --oneline --graph --decorate --all -12
git remote -v
git remote add origin https://github.com/rainrunner20/ForesightAI.git
git push -u origin main
git push origin feature/research-engine feature/dashboard-ui feature/docs-ci
```

If an `origin` remote already exists, inspect it before replacing anything. If the ZIP tool removed the hidden `.git` directory, the local commit history cannot be restored from ordinary source files; extract the ZIP with the built-in Windows extraction tool or 7-Zip and show hidden files.

## Step 3 — collaborate on new work

1. Add teammates as collaborators under repository Settings → Collaborators, once their GitHub usernames are known.
2. Open Issues for the next substantive units of work, such as data ingestion, baseline stance classifier, token-matched controls, citation support auditing, and optional NetLogo adapter.
3. Branch from `main`, commit real increments, open PRs, review, and squash merge where appropriate.
4. Preserve feature branches after merging, per the team workflow.

The baseline scaffold's historical branches are merged locally to `main` already; **do not open PRs claiming that old, already-merged work still needs review.** New PRs should be for new work.
