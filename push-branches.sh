#!/bin/bash
# Aegis OS Multi-Repo Push Script
# - Main branch -> AegisOS repo (new)
# - Preview branches -> AegisOSRepo (tools only, not full repo)

if [ -z "$GITHUB_PAT" ]; then
    export GITHUB_PAT=$(printenv GITHUB_PAT)
fi

if [ -z "$GITHUB_PAT" ]; then
    echo "ERROR: GITHUB_PAT is empty."
    echo "Run with: GITHUB_PAT=your_token ./push-branches.sh"
    exit 1
fi

echo "Token found (length: ${#GITHUB_PAT})"

MAIN_REPO="https://${GITHUB_PAT}@github.com/DeQuackDealer/AegisOS.git"
PREVIEW_REPO="https://${GITHUB_PAT}@github.com/DeQuackDealer/AegisOSRepo.git"

echo ""
echo "=========================================="
echo "STEP 1: Push main branch to AegisOS repo"
echo "=========================================="
git add .
git commit -m "Aegis OS v1.0.0 - Full distribution" || true
git push $MAIN_REPO main --force
echo "Main branch pushed to: https://github.com/DeQuackDealer/AegisOS"

echo ""
echo "=========================================="
echo "STEP 2: Delete main from AegisOSRepo"
echo "=========================================="
git push $PREVIEW_REPO --delete main 2>/dev/null || echo "main already deleted or doesn't exist in AegisOSRepo"

echo ""
echo "=========================================="
echo "STEP 3: Push base-os (tools only)"
echo "=========================================="
git checkout --orphan temp-base
git rm -rf . 2>/dev/null || true
cp -r preview-branches/base-os/* .
git add .
git commit -m "Base OS Tools - Core desktop, themes, license system"
git push $PREVIEW_REPO temp-base:preview/base-os --force
git checkout main
git branch -D temp-base 2>/dev/null || true
echo "preview/base-os pushed (tools only)"

echo ""
echo "=========================================="
echo "STEP 4: Push gamer (tools only)"
echo "=========================================="
git checkout --orphan temp-gamer
git rm -rf . 2>/dev/null || true
cp -r preview-branches/gamer/* .
git add .
git commit -m "Gamer Tools - Upscalers, launchers, streaming, performance"
git push $PREVIEW_REPO temp-gamer:preview/gamer --force
git checkout main
git branch -D temp-gamer 2>/dev/null || true
echo "preview/gamer pushed (tools only)"

echo ""
echo "=========================================="
echo "STEP 5: Push aidev (tools only)"
echo "=========================================="
git checkout --orphan temp-aidev
git rm -rf . 2>/dev/null || true
cp -r preview-branches/aidev/* .
git add .
git commit -m "AI Developer Tools - ML studio, GPU tools, inference"
git push $PREVIEW_REPO temp-aidev:preview/aidev --force
git checkout main
git branch -D temp-aidev 2>/dev/null || true
echo "preview/aidev pushed (tools only)"

echo ""
echo "=========================================="
echo "STEP 6: Cleanup old branches"
echo "=========================================="
git push $PREVIEW_REPO --delete preview/freemium 2>/dev/null || echo "freemium already gone"

echo ""
echo "=========================================="
echo "DONE!"
echo "=========================================="
echo ""
echo "Repository structure:"
echo "  AegisOS (main repo):"
echo "    - https://github.com/DeQuackDealer/AegisOS"
echo "    - Contains: Full OS, build system, website, all editions"
echo ""
echo "  AegisOSRepo (preview/contributions):"
echo "    - https://github.com/DeQuackDealer/AegisOSRepo"
echo "    - preview/base-os: Base OS tools only"
echo "    - preview/gamer: Gaming tools only"
echo "    - preview/aidev: AI tools only"
echo ""
echo "Contributors can work on specific tools without the full repo!"
