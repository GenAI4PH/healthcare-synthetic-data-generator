---
name: setup-synthea
description: Install a pinned official Synthea version on Windows, macOS, or Linux after approval.
---

# Install the official Synthea engine

1. Open `AGENTS.md` and `config/generator.yaml`. Check `synthea.version` is a known, reviewed upstream release tag or a full 40-character commit SHA. If unset, ask the user to select one; don't invent a version.
2. Run `hsg doctor`. If Git or Java 17+ is missing, explain OS-specific install options. Obtain explicit approval before installing system packages. The CLI does **not** install system packages.
3. Run `hsg setup-synthea` to show source, pinned revision and target without downloading anything.
4. Explain network access, disk usage and possible overwrite/checkout effects. Once approved, run `hsg setup-synthea --approve`.
5. Confirm the returned commit SHA and `external/synthea-install.json` (ignored by git). The installation is a detached, pinned checkout under `external/`, never committed.
6. Do not claim patient generation works until a separate upstream smoke test has actually succeeded. Never upload or publish anything without separate authorization.
7. Optionally offer an authentic, editable GitHub Discussion feedback draft; never publish automatically or condition setup on feedback.

## Windows VS Code / PowerShell

```powershell
python -m pip install -e ".[dev]"
hsg doctor
# Edit synthea.version in config/generator.yaml to a verified tag or full SHA
hsg setup-synthea
hsg setup-synthea --approve
```

## macOS / Linux

Use the same CLI after installing Python 3.11+, Git, and Java 17+. The script invokes Git and Java using their platform-native PATH locations and uses no Bash-specific commands.
