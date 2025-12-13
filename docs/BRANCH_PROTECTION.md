# Branch Protection Rules for Aegis OS

This document explains how to set up branch protection rules on GitHub to prevent accidental damage to the main codebase.

## Overview

| Branch | Protection Level | Who Can Push |
|--------|-----------------|--------------|
| `main` | **Maximum** | Maintainers only via PR |
| `preview/freemium` | **Moderate** | Contributors via PR |
| `preview/gamer` | **Moderate** | Contributors via PR |
| `preview/aidev` | **Moderate** | Contributors via PR |

---

## Setting Up Branch Protection on GitHub

### Step 1: Go to Repository Settings

1. Navigate to your repository on GitHub
2. Click **Settings** tab
3. In the left sidebar, click **Branches**

### Step 2: Add Branch Protection Rule

Click **Add rule** and configure as follows:

---

## Rules for `main` Branch

**Branch name pattern:** `main`

### Required Settings (CHECK ALL):

- [x] **Require a pull request before merging**
  - [x] Require approvals: **2**
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners

- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging

- [x] **Require conversation resolution before merging**

- [x] **Require signed commits** (optional but recommended)

- [x] **Require linear history**

- [x] **Do not allow bypassing the above settings**

- [x] **Restrict who can push to matching branches**
  - Add only repository owner/maintainers

- [x] **Allow force pushes** - **UNCHECKED** (Never allow)

- [x] **Allow deletions** - **UNCHECKED** (Never allow)

---

## Rules for Preview Branches

**Branch name pattern:** `preview/*`

This single rule covers all preview branches.

### Required Settings:

- [x] **Require a pull request before merging**
  - [x] Require approvals: **1**
  - [x] Dismiss stale pull request approvals when new commits are pushed

- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging

- [x] **Require conversation resolution before merging**

- [ ] **Require signed commits** - Optional

- [ ] **Require linear history** - Optional

- [x] **Do not allow bypassing the above settings**

- [x] **Allow force pushes** - **UNCHECKED**

- [x] **Allow deletions** - **UNCHECKED**

---

## CODEOWNERS File

Create a `CODEOWNERS` file to automatically assign reviewers:

```
# Default owner for everything
* @DeQuackDealer

# Build system requires owner approval
/build-system/ @DeQuackDealer
/.github/ @DeQuackDealer

# Edition-specific owners (add trusted contributors)
/docs/freemium/ @DeQuackDealer
/docs/gamer/ @DeQuackDealer
/docs/aidev/ @DeQuackDealer
```

Place this file at `.github/CODEOWNERS`

---

## Why These Rules Matter

### Preventing Accidental Damage

1. **No direct pushes to main** - All changes go through review
2. **Required approvals** - At least one person reviews before merge
3. **Status checks** - Automated tests must pass
4. **No force pushes** - History cannot be rewritten
5. **No deletions** - Branches cannot be accidentally deleted

### Maintaining Code Quality

1. **Pull Request workflow** - Encourages discussion
2. **Code review** - Catches bugs early
3. **Conversation resolution** - All concerns addressed
4. **Up-to-date branches** - No merge conflicts

---

## Emergency Procedures

### If Something Goes Wrong

1. **Don't panic** - Git has history
2. **Contact maintainer** - @DeQuackDealer
3. **Use git revert** - Not force push
4. **Document the issue** - Create an Issue on GitHub

### Maintainer Override

In rare emergencies, the repository owner can:
1. Temporarily disable branch protection
2. Make the necessary fix
3. Re-enable protection immediately
4. Document what happened in an Issue

---

## Syncing Preview Branches with Main

Periodically, preview branches should be updated from main:

```bash
# As a maintainer
git checkout preview/freemium
git pull origin preview/freemium
git merge main
git push origin preview/freemium
```

This is done by maintainers, not contributors.

---

## Questions?

Open a Discussion on GitHub if you have questions about branch protection or contributing.
