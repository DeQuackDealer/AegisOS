#!/bin/bash
# Aegis OS Push Script - Pushes to main GitHub repository
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

# Remove duplicate workflow file if it exists
if [ -f ".github/workflows/build-aegis-iso.yml" ]; then
    echo "Removing duplicate workflow file..."
    rm -f .github/workflows/build-aegis-iso.yml
fi

# Repository URL
MAIN_REPO="https://${GITHUB_PAT}@github.com/DeQuackDealer/AegisOS.git"

# Make sure we're on main branch
git checkout main 2>/dev/null || git checkout -b main

# Stage all changes
git add -A

# Commit (ignore if nothing to commit)
git commit -m "Aegis OS v1.0.0 - $(date +%Y-%m-%d)" 2>/dev/null || echo "No new changes to commit"

echo "=========================================="
echo "Pushing to Main Repository (AegisOS)"
echo "=========================================="
echo ""
echo "Pushing to: https://github.com/DeQuackDealer/AegisOS"
if git push "${MAIN_REPO}" main --force; then
    echo "Push: SUCCESS"
else
    echo "Push: FAILED"
    exit 1
fi

echo ""
echo "=========================================="
echo "COMPLETE!"
echo "=========================================="
echo ""
echo "Repository updated: https://github.com/DeQuackDealer/AegisOS"
echo ""
echo "To build ISOs:"
echo "  1. Go to: https://github.com/DeQuackDealer/AegisOS/actions"
echo "  2. Click 'Build Aegis OS ISOs'"
echo "  3. Click 'Run workflow'"
echo "  4. Select which edition to build"
echo ""
