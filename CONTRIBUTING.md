# Contributing

## Required local setup
```bash
make venv.ensure
pip install -U pre-commit
pre-commit install
```

## Before every commit (hooks will run automatically)
```bash
make ssot.env.render
make rules.emit
git add -A
git commit -m "your change"
```

## Guard suite (same as CI)
```bash
make ssot.guards
```

### Troubleshooting
- **Python not in .venv** → `make venv.ensure venv.check`
- **Rules drift** → `make rules.clean rules.emit rules.check`
- **Emergency bypass** (not recommended):  
  `SKIP=venv-check,ssot-guards git commit -m "hotfix"`