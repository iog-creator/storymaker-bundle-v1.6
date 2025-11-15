#!/bin/bash
# Start the dashboard API server
cd "$(dirname "$0")/.."
node tools/server/api.js
