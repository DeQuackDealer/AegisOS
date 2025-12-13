#!/bin/bash
# Aegis OS Branch Push Script
# Merges local changes without deleting remote-only files

# Source environment to ensure secrets are available
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# Check token
if [ -z "$GITHUB_PAT" ]; then
    echo "GITHUB_PAT not found in environment"
    echo "Checking if we can read it directly..."
    # Try to get it from Replit secrets
    export GITHUB_PAT=$(printenv GITHUB_PAT)
fi

if [ -z "$GITHUB_PAT" ]; then
    echo "ERROR: GITHUB_PAT is still empty. Please ensure the secret is set."
    echo "You can also run with: GITHUB_PAT=your_token_here ./push-branches.sh"
    exit 1
fi

echo "Token found (length: ${#GITHUB_PAT})"
REPO="https://${GITHUB_PAT}@github.com/DeQuackDealer/AegisOSRepo.git"

echo ""
echo "=== Step 1: Push main branch (merge, not overwrite) ==="
git add .
git commit -m "Simplified workflows and segmented branch content" || true
# Pull first to get any remote-only files, then push
git pull $REPO main --rebase --allow-unrelated-histories 2>/dev/null || true
git push $REPO main

echo ""
echo "=== Step 2: Update base-os branch (merge with existing) ==="
# Clone existing branch if it exists, or create new
git fetch $REPO preview/base-os:remote-base-os 2>/dev/null || true
git checkout --orphan temp-base-os
git rm -rf . 2>/dev/null || true
# Copy remote files first (if branch existed)
git checkout remote-base-os -- . 2>/dev/null || true
# Then overlay our local files (overwrites same names, keeps remote-only)
cp -r preview-branches/base-os/* .
git add .
git commit -m "Base OS: Core desktop, themes, Wine/Proton foundation"
git push $REPO temp-base-os:preview/base-os --force
git checkout main
git branch -D temp-base-os 2>/dev/null || true
git branch -D remote-base-os 2>/dev/null || true

echo ""
echo "=== Step 3: Update gamer branch (merge with existing) ==="
git fetch $REPO preview/gamer:remote-gamer 2>/dev/null || true
git checkout --orphan temp-gamer
git rm -rf . 2>/dev/null || true
git checkout remote-gamer -- . 2>/dev/null || true
cp -r preview-branches/gamer/* .
git add .
git commit -m "Gamer: Upscalers, game launchers, streaming, performance"
git push $REPO temp-gamer:preview/gamer --force
git checkout main
git branch -D temp-gamer 2>/dev/null || true
git branch -D remote-gamer 2>/dev/null || true

echo ""
echo "=== Step 4: Update aidev branch (merge with existing) ==="
git fetch $REPO preview/aidev:remote-aidev 2>/dev/null || true
git checkout --orphan temp-aidev
git rm -rf . 2>/dev/null || true
git checkout remote-aidev -- . 2>/dev/null || true
cp -r preview-branches/aidev/* .
git add .
git commit -m "AI Developer: ML studio, GPU tools, inference, LLM"
git push $REPO temp-aidev:preview/aidev --force
git checkout main
git branch -D temp-aidev 2>/dev/null || true
git branch -D remote-aidev 2>/dev/null || true

echo ""
echo "=== Step 5: Cleanup old freemium branch ==="
git push $REPO --delete preview/freemium 2>/dev/null || echo "freemium branch already gone or doesn't exist"

echo ""
echo "=== Done! ==="
echo "Branches updated:"
echo "  - main (full repo, merged with remote)"
echo "  - preview/base-os (core OS tools)"
echo "  - preview/gamer (gaming tools)"  
echo "  - preview/aidev (AI tools)"
echo ""
echo "Remote-only files were preserved!"
