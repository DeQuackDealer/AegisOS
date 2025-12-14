#!/bin/bash
# Aegis OS Push Script - Pushes to GitHub
# Usage: GITHUB_PAT=your_token ./push-branches.sh

# Check for token
if [ -z "${GITHUB_PAT}" ]; then
    echo "ERROR: GITHUB_PAT is not set"
    echo ""
    echo "Usage: GITHUB_PAT=your_token ./push-branches.sh"
    echo ""
    echo "To get a token:"
    echo "1. Go to GitHub > Settings > Developer Settings > Personal Access Tokens"
    echo "2. Create a token with 'repo' permissions"
    exit 1
fi

echo "GitHub token found (${#GITHUB_PAT} characters)"
echo ""

# Repository URLs
MAIN_REPO="https://${GITHUB_PAT}@github.com/DeQuackDealer/AegisOS.git"

echo "=========================================="
echo "Pushing to GitHub"
echo "=========================================="

# Make sure we're on main branch
git checkout main 2>/dev/null || git checkout -b main

# Stage all changes
git add -A

# Commit (ignore if nothing to commit)
git commit -m "Aegis OS v1.0.0 - $(date +%Y-%m-%d)" 2>/dev/null || echo "No new changes to commit"

# Push to GitHub
echo ""
echo "Pushing to: https://github.com/DeQuackDealer/AegisOS"
if git push "${MAIN_REPO}" main --force; then
    echo ""
    echo "=========================================="
    echo "SUCCESS!"
    echo "=========================================="
    echo ""
    echo "Your code is now on GitHub:"
    echo "  https://github.com/DeQuackDealer/AegisOS"
    echo ""
    echo "To build ISOs:"
    echo "  1. Go to: https://github.com/DeQuackDealer/AegisOS/actions"
    echo "  2. Click 'Build Aegis OS ISOs'"
    echo "  3. Click 'Run workflow'"
    echo "  4. Select which edition to build"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "FAILED TO PUSH"
    echo "=========================================="
    echo ""
    echo "Possible issues:"
    echo "  - Token doesn't have 'repo' permissions"
    echo "  - Repository doesn't exist yet (create it on GitHub first)"
    echo "  - Network issue"
    exit 1
fi
