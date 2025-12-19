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
    echo "2. Create a Classic token with 'repo' permissions"
    exit 1
fi

echo "GitHub token found (${#GITHUB_PAT} characters)"
echo ""

# Remove duplicate workflow file if it exists
if [ -f ".github/workflows/build-aegis-iso.yml" ]; then
    echo "Removing duplicate workflow file..."
    rm -f .github/workflows/build-aegis-iso.yml
fi

# Clear any cached credentials that might interfere
git config --unset-all credential.helper 2>/dev/null || true
rm -f ~/.git-credentials 2>/dev/null || true

# Set git identity if not set
git config user.email "dequackdealer@aegis.os" 2>/dev/null || true
git config user.name "DeQuackDealer" 2>/dev/null || true

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

# Use token directly in URL (most reliable method)
PUSH_URL="https://DeQuackDealer:${GITHUB_PAT}@github.com/DeQuackDealer/AegisOS.git"

if git push "${PUSH_URL}" main --force 2>&1; then
    echo ""
    echo "Push: SUCCESS"
else
    echo ""
    echo "Push: FAILED"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure you're using a CLASSIC token (not fine-grained)"
    echo "2. Token needs 'repo' scope checked"
    echo "3. Token must not be expired"
    echo "4. Make sure the repo exists: https://github.com/DeQuackDealer/AegisOS"
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
