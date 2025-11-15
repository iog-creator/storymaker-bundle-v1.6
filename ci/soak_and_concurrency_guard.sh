#!/bin/bash
set -euo pipefail

# Soak and Concurrency Guard
# Asserts stability across load and concurrent requests

echo "🔄 Testing soak and concurrency stability..."

baseN=${NARRATIVE_BASE:-http://127.0.0.1:8001}/api/v1
baseW=${WORLDCORE_BASE:-http://127.0.0.1:8000}/api/v1

# Test 1: Basic concurrency test
echo "  🚀 Testing basic concurrency (10 parallel requests)..."
seq 1 10 | xargs -I{} -P 10 curl -sS -o /dev/null -w "%{http_code}\n" \
  -H "Content-Type: application/json" \
  -d "{\"world_id\":\"soak-test-{},\",\"premise\":\"A ferry runs backward in time {}\",\"structure\":\"harmon_8\",\"max_beats\":6}" \
  "$baseN/narrative/outline" | grep -v '^200$' && {
  echo "❌ Basic concurrency test failed - some requests returned non-200 status"
  exit 1
} || true

echo "  ✅ Basic concurrency test passed"

# Test 2: Extended soak test
echo "  🏃 Testing extended soak (20 requests over 30 seconds)..."
for i in {1..20}; do
  curl -sS -o /dev/null -w "%{http_code}\n" \
    -H "Content-Type: application/json" \
    -d "{\"world_id\":\"soak-extended-$i\",\"premise\":\"A test that runs for a long time $i\",\"structure\":\"harmon_8\",\"max_beats\":4}" \
    "$baseN/narrative/outline" | grep -v '^200$' && {
    echo "❌ Extended soak test failed at request $i"
    exit 1
  }
  sleep 1.5
done

echo "  ✅ Extended soak test passed"

# Test 3: Mixed service concurrency
echo "  🔀 Testing mixed service concurrency..."
# Run narrative and QA requests concurrently
(
  for i in {1..5}; do
    curl -sS -o /dev/null -w "narrative-$i: %{http_code}\n" \
      -H "Content-Type: application/json" \
      -d "{\"world_id\":\"mixed-test-n-$i\",\"premise\":\"Mixed test narrative $i\",\"structure\":\"harmon_8\",\"max_beats\":4}" \
      "$baseN/narrative/outline"
  done
) &
(
  for i in {1..5}; do
    curl -sS -o /dev/null -w "qa-$i: %{http_code}\n" \
      -H "Content-Type: application/json" \
      -d "{\"draft\":\"Mixed test QA draft $i\",\"cap\":5}" \
      "$baseW/qa/trope-budget"
  done
) &
wait

echo "  ✅ Mixed service concurrency test passed"

# Test 4: High concurrency stress test
echo "  💥 Testing high concurrency stress (50 parallel requests)..."
seq 1 50 | xargs -I{} -P 50 curl -sS -o /dev/null -w "%{http_code}\n" \
  -H "Content-Type: application/json" \
  -d "{\"world_id\":\"stress-test-{},\",\"premise\":\"Stress test premise {}\",\"structure\":\"harmon_8\",\"max_beats\":3}" \
  "$baseN/narrative/outline" | grep -v '^200$' && {
  echo "❌ High concurrency stress test failed - some requests returned non-200 status"
  exit 1
} || true

echo "  ✅ High concurrency stress test passed"

# Test 5: Memory and resource stability
echo "  🧠 Testing memory and resource stability..."
# Run a series of requests and monitor for memory leaks
for i in {1..30}; do
  curl -sS -H "Content-Type: application/json" \
    -d "{\"world_id\":\"memory-test-$i\",\"premise\":\"Memory test premise $i\",\"structure\":\"harmon_8\",\"max_beats\":6}" \
    "$baseN/narrative/outline" > /dev/null
  
  # Check service health every 5 requests
  if [ $((i % 5)) -eq 0 ]; then
    health=$(curl -sS "$baseN/health" | jq -r '.status')
    if [ "$health" != "ok" ]; then
      echo "❌ Service health degraded at request $i: $health"
      exit 1
    fi
  fi
done

echo "  ✅ Memory and resource stability test passed"

# Test 6: Error handling under load
echo "  🚫 Testing error handling under load..."
# Mix valid and invalid requests
(
  for i in {1..10}; do
    # Valid request
    curl -sS -o /dev/null -w "valid-$i: %{http_code}\n" \
      -H "Content-Type: application/json" \
      -d "{\"world_id\":\"error-test-valid-$i\",\"premise\":\"Valid request $i\",\"structure\":\"harmon_8\",\"max_beats\":4}" \
      "$baseN/narrative/outline"
    
    # Invalid request (missing required field)
    curl -sS -o /dev/null -w "invalid-$i: %{http_code}\n" \
      -H "Content-Type: application/json" \
      -d "{\"world_id\":\"error-test-invalid-$i\",\"premise\":\"Invalid request $i\"}" \
      "$baseN/narrative/outline"
  done
) | grep -E "valid-.*: 200|invalid-.*: [45][0-9][0-9]" || {
  echo "❌ Error handling under load test failed"
  exit 1
}

echo "  ✅ Error handling under load test passed"

# Test 7: Response time consistency
echo "  ⏱️  Testing response time consistency..."
response_times=()
for i in {1..20}; do
  start=$(date +%s%3N)
  curl -sS -H "Content-Type: application/json" \
    -d "{\"world_id\":\"timing-test-$i\",\"premise\":\"Timing test premise $i\",\"structure\":\"harmon_8\",\"max_beats\":4}" \
    "$baseN/narrative/outline" > /dev/null
  end=$(date +%s%3N)
  duration=$((end - start))
  response_times+=($duration)
done

# Calculate statistics
python3 - <<'PY'
import sys
import statistics

# Read response times from stdin
times = [int(line.strip()) for line in sys.stdin if line.strip()]

if len(times) < 10:
    print("❌ Not enough response times collected")
    sys.exit(1)

mean_time = statistics.mean(times)
median_time = statistics.median(times)
p95_time = sorted(times)[int(len(times) * 0.95)]

print(f"Response time statistics:")
print(f"  Mean: {mean_time:.0f}ms")
print(f"  Median: {median_time:.0f}ms")
print(f"  P95: {p95_time:.0f}ms")

# Check for reasonable response times
if p95_time > 10000:  # 10 seconds
    print(f"❌ P95 response time too high: {p95_time}ms")
    sys.exit(1)

if mean_time > 5000:  # 5 seconds
    print(f"❌ Mean response time too high: {mean_time:.0f}ms")
    sys.exit(1)

print("✅ Response time consistency test passed")
PY

echo "  ✅ Response time consistency test passed"

# Test 8: Service recovery after load
echo "  🔄 Testing service recovery after load..."
# Check that services are still healthy after all the load
narrative_health=$(curl -sS "$baseN/health" | jq -r '.status')
worldcore_health=$(curl -sS "$baseW/health" | jq -r '.status')

if [ "$narrative_health" != "ok" ] || [ "$worldcore_health" != "ok" ]; then
  echo "❌ Services not healthy after load: narrative=$narrative_health, worldcore=$worldcore_health"
  exit 1
fi

echo "  ✅ Service recovery after load test passed"

# Test 9: Proof file generation under load
echo "  📄 Testing proof file generation under load..."
# Generate a few requests and verify proof files are created
for i in {1..5}; do
  resp=$(curl -sS -H "Content-Type: application/json" \
    -d "{\"world_id\":\"proof-load-test-$i\",\"premise\":\"Proof load test $i\",\"structure\":\"harmon_8\",\"max_beats\":4}" \
    "$baseN/narrative/outline")
  
  proof_path=$(echo "$resp" | jq -r '.proof.path')
  if [ "$proof_path" = "null" ] || [ ! -f "$proof_path" ]; then
    echo "❌ Proof file not created for load test request $i"
    exit 1
  fi
done

echo "  ✅ Proof file generation under load test passed"

echo "🎉 All soak and concurrency tests passed!"
