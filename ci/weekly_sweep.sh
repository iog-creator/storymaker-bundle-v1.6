#!/usr/bin/env bash
set -euo pipefail
make services.up
REQ_OK=${REQ_OK:-3} make guards.health
make guards.proof
make workspaces.guards
