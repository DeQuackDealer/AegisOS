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
    echo "2. Create a Fine-grained token or Classic token with 'repo' permissions"
    exit 1
fi

echo "GitHub token found (${#GITHUB_PAT} characters)"
echo ""

# Remove duplicate workflow file if it exists
if [ -f ".github/workflows/build-aegis-iso.yml" ]; then
    echo "Removing duplicate workflow file..."
    rm -f .github/workflows/build-aegis-iso.yml
fi

# Configure git to use token (prevents password prompt)
git config --local credential.helper store
echo "https://DeQuackDealer:${GITHUB_PAT}@github.com" > ~/.git-credentials

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

# Push using credential helper (no password prompt)
if git push https://github.com/DeQuackDealer/AegisOS.git main --force; then
    echo "Push: SUCCESS"
else
    echo "Push: FAILED"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure your token has 'repo' permissions"
    echo "2. For Fine-grained tokens, ensure it has access to DeQuackDealer/AegisOS"
    echo "3. Try creating a Classic token instead"
    rm -f ~/.git-credentials
    exit 1
fi

# Clean up credentials file
rm -f ~/.git-credentials

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
