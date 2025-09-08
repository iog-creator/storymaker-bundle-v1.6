#!/usr/bin/env bash
# commit_hygiene_check.sh — Check commit message format compliance
# Supports stdin input for batch checking

COMMIT_REGEX="^PR-[0-9][0-9][0-9][0-9]: .*$"

if [[ "$1" == "--stdin" ]]; then
    # Read from stdin and validate each line
    total=0
    matched=0
    while IFS= read -r line; do
        [[ -n "$line" ]] || continue
        total=$((total + 1))
        if [[ "$line" =~ $COMMIT_REGEX ]]; then
            matched=$((matched + 1))
        fi
    done
    
    if [[ $total -eq 0 ]]; then
        echo '{"status":"error","data":{"window":{"total":0,"matched":0}},"error":{"message":"No input provided"},"meta":{"smoke_score":1.0,"reasons":["no_input"],"scope":["commit_hygiene"],"checks":[],"proofs":[]}}'
    elif [[ $matched -eq $total ]]; then
        echo "{\"status\":\"success\",\"data\":{\"window\":{\"total\":$total,\"matched\":$matched}},\"error\":{\"message\":\"\"},\"meta\":{\"smoke_score\":0.0,\"reasons\":[\"all_matched\"],\"scope\":[\"commit_hygiene\"],\"checks\":[\"regex_ok\"],\"proofs\":[\"commit_check\"]}}"
    else
        echo "{\"status\":\"error\",\"data\":{\"window\":{\"total\":$total,\"matched\":$matched}},\"error\":{\"message\":\"Commit hygiene violation: $((total - matched)) commits do not match pattern\"},\"meta\":{\"smoke_score\":1.0,\"reasons\":[\"hygiene_violation\"],\"scope\":[\"commit_hygiene\"],\"checks\":[],\"proofs\":[]}}"
    fi
else
    # Single mode - check if we're in a git repo and validate recent commits
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        echo '{"status":"warning","data":{},"error":{"message":"Not in a git repository"},"meta":{"smoke_score":0.5,"reasons":["not_git_repo"],"scope":["commit_hygiene"],"checks":[],"proofs":[]}}'
        exit 0
    fi
    
    # Check recent commits (last 10)
    recent_commits=$(git log --oneline -10 --format="%s" 2>/dev/null || echo "")
    if [[ -n "$recent_commits" ]]; then
        echo "$recent_commits" | bash "$0" --stdin
    else
        echo '{"status":"success","data":{},"error":{"message":""},"meta":{"smoke_score":0.0,"reasons":["no_commits"],"scope":["commit_hygiene"],"checks":["no_commits"],"proofs":[]}}'
    fi
fi

