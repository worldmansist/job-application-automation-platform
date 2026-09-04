# GitHub workflow for this project

Below is a basic set of commands for saving and updating the project on GitHub.

## 1. Check the Status

```bash
git status
```

## 2. Add Files to the Index

```bash
git add .
```

Or only selected files:

```bash
git add app README.md requirements.txt
```

## 3. Create a Commit

```bash
git commit -m "Initial project setup"
```

Or after making changes:

```bash
git commit -m "Add application API and schemas"
```

## 4. Connect a GitHub Repository

If the repository has not been created yet:

```bash
git remote add origin https://github.com/<username>/<repo-name>.git
```

Check the connection:

```bash
git remote -v
```

## 5. Push Changes to GitHub

```bash
git push -u origin main
```

If the branch is called `master`:

```bash
git push -u origin master
```

## 6. Further Updates

After each change:

```bash
git status
git add .
git commit -m "Describe your changes"
git push
```

## 7. Create a New Branch

```bash
git checkout -b feature/my-change
```

After finishing:

```bash
git add .
git commit -m "Add my change"
git push -u origin feature/my-change
```

## 8. Update the Local Branch from GitHub

```bash
git pull origin main
```

## 9. Useful Command for Viewing History

```bash
git log --oneline
```

## 10. For Windows PowerShell

To run everything quickly:

```powershell
git status
git add .
git commit -m "Update project"
git push
```

## 11. Quick Template for Current Work

```bash
git add .
git commit -m "Update app routes and schemas"
git push
```

> If `git push` produces an error, it is usually because the repository is not connected yet or the branch does not match the main branch.
