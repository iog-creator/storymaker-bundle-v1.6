#!/bin/bash
echo "Simple test - this should work"
echo "Current time: $(date)"
echo "Working directory: $(pwd)"
echo "Environment check:"
echo "MOCK_LMS: ${MOCK_LMS:-not set}"
echo "POSTGRES_DSN: ${POSTGRES_DSN:-not set}"
echo "Test complete"
