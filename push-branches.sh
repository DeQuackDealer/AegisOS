#!/bin/bash
# Aegis OS Push Script - Pushes to both GitHub repositories
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
PREVIEW_REPO="https://${GITHUB_PAT}@github.com/DeQuackDealer/AegisOSRepo.git"

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
    echo "Main repository push: SUCCESS"
else
    echo "Main repository push: FAILED"
fi

echo ""
echo "=========================================="
echo "Pushing to Preview Repository (AegisOSRepo)"
echo "=========================================="

# Create and push preview branches
for edition in freemium basic gamer workplace aidev gamer-ai server; do
    echo ""
    echo "Creating preview branch: preview-${edition}"
    git checkout -B "preview-${edition}" main
    
    echo "Pushing preview-${edition} to AegisOSRepo..."
    if git push "${PREVIEW_REPO}" "preview-${edition}" --force; then
        echo "  preview-${edition}: SUCCESS"
    else
        echo "  preview-${edition}: FAILED"
    fi
done

# Return to main branch
git checkout main

echo ""
echo "=========================================="
echo "COMPLETE!"
echo "=========================================="
echo ""
echo "Repositories updated:"
echo "  Main:    https://github.com/DeQuackDealer/AegisOS"
echo "  Preview: https://github.com/DeQuackDealer/AegisOSRepo"
echo ""
echo "Preview branches created in AegisOSRepo:"
echo "  - preview-freemium"
echo "  - preview-basic"
echo "  - preview-gamer"
echo "  - preview-workplace"
echo "  - preview-aidev"
echo "  - preview-gamer-ai"
echo "  - preview-server"
echo ""
echo "To build ISOs:"
echo "  1. Go to: https://github.com/DeQuackDealer/AegisOS/actions"
echo "  2. Click 'Build Aegis OS ISOs'"
echo "  3. Click 'Run workflow'"
echo "  4. Select which edition to build"
echo ""
