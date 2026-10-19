# Healthcare Synthetic Data Generator

A cross-platform, AI-agent-friendly **orchestration project** for installing the official [Synthea](https://github.com/synthetichealth/synthea) simulator, configuring runs, validating generated output, and transferring generated files to configured destinations.

**Synthea is not included in this repository.** The installer (Phase 2) will fetch a chosen, pinned official upstream release or source revision into a separate, ignored installation directory. This project does not claim authorship of Synthea.

## Status
Phase 1: repository foundation and local CLI diagnostic commands. Setup, actual generation, and cloud uploads are *planned*, not yet implemented.

## Start (Windows PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
hsg doctor
hsg config-show
pytest
```

## macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
hsg doctor
hsg config-show
pytest
```

## Planned commands (not yet implemented)
```text
hsg setup --mode jar --version <verified-version>
hsg generate csv --patients 10 --state NJ
hsg generate fhir --patients 1000
hsg generate ccda --patients 100000
hsg upload --destination s3
```

## Principles
- Download only from the official upstream Synthea distribution/repository, with pinned versions and checksum verification where available.
- Obtain user approval before installing software, changing machine configuration, or uploading files.
- Never store credentials in YAML or send data without explicit configuration.
- Make the CLI deterministic and testable; agents call it instead of inventing their own shell steps.
- Default to local staging of outputs before upload.
- Record run version/seed/count/configuration in a manifest (future phase).

## License and attribution
This orchestration code is licensed Apache-2.0 (see `LICENSE`). Synthea is an independent upstream project licensed under Apache-2.0; see `THIRD_PARTY_NOTICES.md`. If Synthea is fetched during setup, its own license and notices remain with that installation.

## Phase 2: official Synthea installation (starter)

The setup CLI downloads **only from the official Synthea Git repository** and checks out an immutable commit selected through `config/generator.yaml`. Synthea is stored in `external/synthea`, which is excluded from this project's Git history.

```powershell
python -m pip install -e ".[dev]"
hsg doctor
# Set synthea.version to a reviewed existing Synthea release tag or full 40-character SHA.
hsg setup-synthea              # preview (no network changes)
hsg setup-synthea --approve    # download / checkout, requires user approval
```

Prerequisites: Python 3.11+, Git, and Java 17+. This command does not install prerequisites, compile Synthea, generate patients, or upload files. Those are separate approved steps in future work. In VS Code, create `feature/phase2-synthea-setup` locally before copying or committing these changes.
