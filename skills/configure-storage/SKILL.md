---
name: configure-storage
description: Preview and optionally upload an existing completed synthetic dataset to local, S3, Azure Blob, or Google Drive after separate approval.
---
# Storage configuration and upload
1. Read `AGENTS.md`, `docs/PHASE-4.md` and `config/storage.yaml`.
2. Select provider, validate destination and confirm run directory includes completed `manifest.json`.
3. Do not put keys, secrets or auth tokens into YAML or git. Use credential chains and least-privilege roles.
4. Run `hsg storage-plan <run-dir> [--provider ...]`; report exact file count, bytes and destination.
5. Obtain explicit user approval for remote uploads. Preview `hsg upload <run-dir> [--provider ...]` before `--approve`.
6. Run the approved command, verify the receipt and report any partial remote upload failures. Do not delete remotely or retry blindly.
7. Never post user feedback to GitHub automatically.
