---
name: release-maintenance
description: Validate and document tagged software releases without bundling synthetic data or official Synthea.
---
# Release maintenance

Read `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md` and `CHANGELOG.md`. Run `python -m pytest -q` and review CI status. Verify one opt-in local smoke test before claiming upstream integration; check version/tag consistency and known limitations. Never add generated patient datasets or credentials. Obtain explicit approval before pushing tags or publishing GitHub releases.
