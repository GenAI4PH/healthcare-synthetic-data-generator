---
name: configure-storage
description: Plan and approve local or S3 uploads of completed synthetic-data runs.
---
# Storage configuration and upload

Read `AGENTS.md`, `docs/configuration.md` and `config/storage.yaml`. Confirm that the source has a completed `manifest.json`, then preview via `hsg storage-plan RUN_DIR --provider s3` (or `local`). Explain destination and size, request explicit approval, then run `hsg upload RUN_DIR --provider s3 --approve`. Review the receipt and disclose any partial-upload errors. Use IAM/SSO credentials, never committed secrets. Azure and Google Drive adapters are experimental and unverified.
