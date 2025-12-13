#!/bin/bash
# Aegis OS Branch Push Script
# Replace YOUR_TOKEN with your GitHub Personal Access Token

TOKEN="YOUR_TOKEN"
REPO="https://${TOKEN}@github.com/DeQuackDealer/AegisOSRepo.git"

echo "=== Step 1: Push main branch ==="
git add .
git commit -m "Simplified workflows and segmented branch content" || true
git push $REPO main --force

echo ""
echo "=== Step 2: Create base-os branch ==="
git checkout --orphan temp-base-os
git rm -rf . 2>/dev/null || true
cp -r preview-branches/base-os/* .
git add .
git commit -m "Base OS: Core desktop, themes, Wine/Proton foundation"
git push $REPO temp-base-os:preview/base-os --force
git checkout main
git branch -D temp-base-os

echo ""
echo "=== Step 3: Create gamer branch ==="
git checkout --orphan temp-gamer
git rm -rf . 2>/dev/null || true
cp -r preview-branches/gamer/* .
git add .
git commit -m "Gamer: Upscalers, game launchers, streaming, performance"
git push $REPO temp-gamer:preview/gamer --force
git checkout main
git branch -D temp-gamer

echo ""
echo "=== Step 4: Create aidev branch ==="
git checkout --orphan temp-aidev
git rm -rf . 2>/dev/null || true
cp -r preview-branches/aidev/* .
git add .
git commit -m "AI Developer: ML studio, GPU tools, inference, LLM"
git push $REPO temp-aidev:preview/aidev --force
git checkout main
git branch -D temp-aidev

echo ""
echo "=== Step 5: Delete old freemium branch ==="
git push $REPO --delete preview/freemium 2>/dev/null || echo "freemium already deleted or doesn't exist"

echo ""
echo "=== Done! ==="
echo "Branches created:"
echo "  - main (full repo)"
echo "  - preview/base-os (core OS tools)"
echo "  - preview/gamer (gaming tools only)"
echo "  - preview/aidev (AI tools only)"
