#!/bin/bash
# Aegis OS Multi-Repo Push Script
# - Main branch -> AegisOS repo (new)
# - Preview branches -> AegisOSRepo (tools only, not full repo)

set -e

if [ -z "${GITHUB_PAT:-}" ]; then
    echo "ERROR: GITHUB_PAT environment variable is not set."
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
git commit -m "Aegis OS v1.0.0 - Full distribution" || echo "Nothing to commit"
git push "${MAIN_REPO}" main --force
echo "Main branch pushed to: https://github.com/DeQuackDealer/AegisOS"

echo ""
echo "=========================================="
echo "STEP 2: Delete main from AegisOSRepo"
echo "=========================================="
git push "${PREVIEW_REPO}" --delete main 2>/dev/null || echo "main already deleted or doesn't exist in AegisOSRepo"

push_preview_branch() {
    local branch_name="$1"
    local source_dir="$2"
    local commit_msg="$3"
    
    echo ""
    echo "=========================================="
    echo "Pushing ${branch_name} (tools only)"
    echo "=========================================="
    
    if [ ! -d "${source_dir}" ]; then
        echo "WARNING: ${source_dir} does not exist, skipping"
        return 0
    fi
    
    git checkout --orphan "temp-${branch_name}" || {
        echo "ERROR: Failed to create orphan branch"
        git checkout main
        return 1
    }
    
    git rm -rf . 2>/dev/null || true
    
    if ! cp -r "${source_dir}"/* . 2>/dev/null; then
        echo "WARNING: No files to copy from ${source_dir}"
        git checkout main
        git branch -D "temp-${branch_name}" 2>/dev/null || true
        return 0
    fi
    
    git add .
    git commit -m "${commit_msg}" || {
        echo "Nothing to commit for ${branch_name}"
        git checkout main
        git branch -D "temp-${branch_name}" 2>/dev/null || true
        return 0
    }
    
    git push "${PREVIEW_REPO}" "temp-${branch_name}:preview/${branch_name}" --force
    git checkout main
    git branch -D "temp-${branch_name}" 2>/dev/null || true
    echo "preview/${branch_name} pushed (tools only)"
}

push_preview_branch "base-os" "preview-branches/base-os" "Base OS Tools - Core desktop, themes, license system"
push_preview_branch "gamer" "preview-branches/gamer" "Gamer Tools - Upscalers, launchers, streaming, performance"
push_preview_branch "aidev" "preview-branches/aidev" "AI Developer Tools - ML studio, GPU tools, inference"

echo ""
echo "=========================================="
echo "STEP 6: Cleanup old branches"
echo "=========================================="
git push "${PREVIEW_REPO}" --delete preview/freemium 2>/dev/null || echo "freemium already gone"

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
