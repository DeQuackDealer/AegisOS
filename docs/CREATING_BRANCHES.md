# Creating Preview Branches on GitHub

This guide explains how to create the preview branches for open-source contributions.

## Step-by-Step Instructions

### 1. Push Main Branch First

Make sure your main branch is pushed to GitHub:
```bash
git push -u origin main
```

### 2. Create Preview Branches Locally

```bash
# Create freemium preview branch
git checkout main
git checkout -b preview/freemium
git push -u origin preview/freemium

# Create gamer preview branch
git checkout main
git checkout -b preview/gamer
git push -u origin preview/gamer

# Create aidev preview branch
git checkout main
git checkout -b preview/aidev
git push -u origin preview/aidev

# Return to main
git checkout main
```

### 3. Set Up Branch Protection on GitHub

Go to your repository on GitHub:

1. Click **Settings**
2. Click **Branches** in the left sidebar
3. Click **Add rule**

#### For `main` branch:

- **Branch name pattern:** `main`
- [x] Require a pull request before merging
  - Require approvals: 2
- [x] Require status checks to pass
- [x] Do not allow bypassing the above settings
- [ ] Allow force pushes (UNCHECKED!)
- [ ] Allow deletions (UNCHECKED!)

#### For preview branches:

- **Branch name pattern:** `preview/*`
- [x] Require a pull request before merging
  - Require approvals: 1
- [x] Require status checks to pass
- [ ] Allow force pushes (UNCHECKED!)
- [ ] Allow deletions (UNCHECKED!)

### 4. Verify Branches Exist

On GitHub, click the branch dropdown. You should see:
- `main`
- `preview/freemium`
- `preview/gamer`
- `preview/aidev`

### 5. Set Default Branch

Keep `main` as the default branch:
1. Settings → Branches
2. Ensure "Default branch" is `main`

---

## Quick Commands Reference

```bash
# List all branches
git branch -a

# Switch to a branch
git checkout preview/freemium

# Update branch from main
git checkout preview/freemium
git merge main
git push origin preview/freemium

# Delete a branch (if needed)
git branch -d branch-name           # Local
git push origin --delete branch-name # Remote
```

---

## Branch Naming Convention

| Branch | Purpose |
|--------|---------|
| `main` | Production code, fully tested |
| `preview/freemium` | Freemium edition development |
| `preview/gamer` | Gamer edition development |
| `preview/aidev` | AI Developer edition development |

---

## Merging Changes

### From Preview to Main

Only maintainers can merge to main:
1. Create PR from preview branch to main
2. Requires 2 approvals
3. All tests must pass
4. Squash and merge recommended

### From Main to Preview

Keep preview branches updated:
```bash
git checkout preview/freemium
git pull origin main
git push origin preview/freemium
```

Do this periodically to avoid large merge conflicts.
