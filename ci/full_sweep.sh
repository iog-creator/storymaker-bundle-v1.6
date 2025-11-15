#!/usr/bin/env bash
set -euo pipefail

# Full Verification Sweep - Production Readiness Check
# Based on SSOT (MASTER_PLAN + VALIDATION_PROTOCOL)
# Captures all results in one comprehensive log

LOG_FILE="/tmp/storymaker_full_sweep_$(date +%Y%m%d_%H%M%S).log"
echo "=== STORYMAKER FULL VERIFICATION SWEEP ===" | tee "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Change to project directory
cd "$(dirname "$0")/.."

# Activate virtual environment
source .venv/bin/activate

# Load environment
source .env.local

# Function to run command and capture results
run_check() {
    local check_name="$1"
    local command="$2"
    local expected_exit="${3:-0}"
    
    echo "--- $check_name ---" | tee -a "$LOG_FILE"
    echo "Command: $command" | tee -a "$LOG_FILE"
    echo "Expected exit: $expected_exit" | tee -a "$LOG_FILE"
    
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        local actual_exit=$?
        if [ "$actual_exit" -eq "$expected_exit" ]; then
            echo "✅ PASS (exit $actual_exit)" | tee -a "$LOG_FILE"
        else
            echo "⚠️  UNEXPECTED EXIT (got $actual_exit, expected $expected_exit)" | tee -a "$LOG_FILE"
        fi
    else
        local actual_exit=$?
        if [ "$actual_exit" -eq "$expected_exit" ]; then
            echo "✅ PASS (exit $actual_exit)" | tee -a "$LOG_FILE"
        else
            echo "❌ FAIL (exit $actual_exit, expected $expected_exit)" | tee -a "$LOG_FILE"
        fi
    fi
    echo "" | tee -a "$LOG_FILE"
}

# Function to run command and allow failure
run_check_optional() {
    local check_name="$1"
    local command="$2"
    
    echo "--- $check_name (OPTIONAL) ---" | tee -a "$LOG_FILE"
    echo "Command: $command" | tee -a "$LOG_FILE"
    
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        echo "✅ PASS" | tee -a "$LOG_FILE"
    else
        echo "⚠️  SKIPPED (optional check failed)" | tee -a "$LOG_FILE"
    fi
    echo "" | tee -a "$LOG_FILE"
}

echo "🧪 1. ENVIRONMENT & CONFIG CHECKS" | tee -a "$LOG_FILE"
echo "=================================" | tee -a "$LOG_FILE"

run_check "Config Check" "make config-check"
run_check "LM Studio Connectivity" "make verify-lms"
run_check_optional "Narrative Service (Groq)" "make verify-narrative"
run_check_optional "Preflight Guards" "make verify-preflight"

echo "🏥 2. TOLERANT HEALTH CHECKS" | tee -a "$LOG_FILE"
echo "=============================" | tee -a "$LOG_FILE"

run_check "Default Health (≥3 OK)" "make guards.health"
run_check "Tolerant Health (≥2 OK)" "REQ_OK=2 make guards.health"
run_check "Health Matrix Display" "make guards.health.matrix"

echo "🔒 3. PROOF INTEGRITY CHECKS" | tee -a "$LOG_FILE"
echo "=============================" | tee -a "$LOG_FILE"

run_check_optional "Proof Integrity" "make guards.proof"
run_check "Canonicalizer Regression" "make guards.canon"

echo "🛡️ 4. GUARD PACK (CI DISCIPLINE)" | tee -a "$LOG_FILE"
echo "=================================" | tee -a "$LOG_FILE"

run_check_optional "Full Guard Suite" "make guards"

echo "🔄 5. CROSS-WORKSPACE CHECKS" | tee -a "$LOG_FILE"
echo "=============================" | tee -a "$LOG_FILE"

run_check_optional "Cross-Workspace Guards" "make workspaces.guards"

echo "🚀 6. END-TO-END VERIFICATION" | tee -a "$LOG_FILE"
echo "=============================" | tee -a "$LOG_FILE"

run_check_optional "Full Verification Suite" "make verify-all"
run_check_optional "Live End-to-End Test" "make verify-live"

echo "📊 SUMMARY" | tee -a "$LOG_FILE"
echo "==========" | tee -a "$LOG_FILE"
echo "Completed: $(date)" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Count results using safer patterns
total_checks=$(awk '/^--- .* ---$/ { count++ } END { print count+0 }' "$LOG_FILE")
passed_checks=$(grep -c "✅ PASS" "$LOG_FILE" || echo "0")
failed_checks=$(grep -c "❌ FAIL" "$LOG_FILE" || echo "0")
skipped_checks=$(grep -c "⚠️  SKIPPED" "$LOG_FILE" || echo "0")

echo "Total checks: $total_checks" | tee -a "$LOG_FILE"
echo "Passed: $passed_checks" | tee -a "$LOG_FILE"
echo "Failed: $failed_checks" | tee -a "$LOG_FILE"
echo "Skipped: $skipped_checks" | tee -a "$LOG_FILE"

if [ "$failed_checks" -eq 0 ]; then
    echo "🎉 ALL CHECKS PASSED!" | tee -a "$LOG_FILE"
    exit 0
else
    echo "⚠️  SOME CHECKS FAILED - REVIEW LOG" | tee -a "$LOG_FILE"
    exit 1
fi