#!/bin/bash
# Mock commit hygiene check for development

if [[ "$1" == "--stdin" ]]; then
    # Read from stdin and count lines
    total=0
    matched=0
    while IFS= read -r line; do
        total=$((total + 1))
        if [[ "$line" =~ ^PR-[0-9]{4}: ]]; then
            matched=$((matched + 1))
        fi
    done
    
    if [[ $matched -eq $total ]] && [[ $total -gt 0 ]]; then
        echo "{\"status\":\"success\",\"data\":{\"window\":{\"total\":$total,\"matched\":$matched}},\"error\":{\"message\":\"\"},\"meta\":{\"smoke_score\":0.0,\"reasons\":[\"all_matched\"],\"scope\":[\"commit_hygiene\"],\"checks\":[\"regex_ok\"],\"proofs\":[\"commit_check\"]}}"
    else
        echo "{\"status\":\"error\",\"data\":{\"window\":{\"total\":$total,\"matched\":$matched}},\"error\":{\"message\":\"Commit hygiene violation\"},\"meta\":{\"smoke_score\":1.0,\"reasons\":[\"hygiene_violation\"],\"scope\":[\"commit_hygiene\"],\"checks\":[],\"proofs\":[]}}"
    fi
else
    echo "{\"status\":\"success\",\"data\":{\"hygiene\":\"ok\"},\"error\":{\"message\":\"\"},\"meta\":{\"smoke_score\":0.0,\"reasons\":[\"mock_mode\"],\"scope\":[\"commit_hygiene\"],\"checks\":[\"mock\"],\"proofs\":[\"mock\"]}}"
fi
