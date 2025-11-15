#!/usr/bin/env bash
# ssot_presence.sh — Check SSOT (Single Source of Truth) file presence
# Configurable count expectation for different project types

SSOT_DIR="${SSOT_DIR:-docs/SSOT}"
EXPECTED_COUNT="${SSOT_EXPECTED_COUNT:-16}"

# Count SSOT files
count=$(find "$SSOT_DIR" -name "*.md" 2>/dev/null | wc -l)

if [[ $count -gt 0 ]]; then
    # Check if count matches expectation (with some flexibility)
    if [[ $count -ge $EXPECTED_COUNT ]] || [[ $count -ge 1 && $EXPECTED_COUNT -gt 16 ]]; then
        echo "{\"status\":\"success\",\"data\":{\"count\":$count,\"expected\":$EXPECTED_COUNT},\"error\":{\"message\":\"\"},\"meta\":{\"smoke_score\":0.0,\"reasons\":[\"ssot_found\"],\"scope\":[\"ssot_presence\"],\"checks\":[\"count_ok\"],\"proofs\":[\"ssot_files\"]}}"
    else
        echo "{\"status\":\"warning\",\"data\":{\"count\":$count,\"expected\":$EXPECTED_COUNT},\"error\":{\"message\":\"SSOT count below expected\"},\"meta\":{\"smoke_score\":0.5,\"reasons\":[\"ssot_count_low\"],\"scope\":[\"ssot_presence\"],\"checks\":[\"count_low\"],\"proofs\":[\"ssot_files\"]}}"
    fi
else
    echo "{\"status\":\"error\",\"data\":{\"count\":0,\"expected\":$EXPECTED_COUNT},\"error\":{\"message\":\"No SSOT files found in $SSOT_DIR\"},\"meta\":{\"smoke_score\":1.0,\"reasons\":[\"no_ssot\"],\"scope\":[\"ssot_presence\"],\"checks\":[],\"proofs\":[]}}"
fi
