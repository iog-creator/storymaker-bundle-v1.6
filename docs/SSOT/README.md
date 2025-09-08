# StoryMaker SSOT (Single Source of Truth)

This directory contains the authoritative documentation and specifications for the StoryMaker project.

## Core Documents

- **AGENTS.md** - Main agent instructions and rules
- **StoryMaker_SRS_v1.1.md** - Software Requirements Specification
- **Acceptance_Tests_v1.md** - Acceptance criteria and test specifications

## Integration with AgentPM

This project now integrates with the AgentPM workspace system for:
- Local-first AI verification via LM Studio
- Envelope-based response validation
- Automated quality gates and preflight checks
- Graph-RAG capabilities for documentation analysis

## Usage

Run verification checks:
```bash
make verify-all
```

Test LM Studio integration:
```bash
make verify-lms
```

Run preflight checks:
```bash
make verify-preflight
```
