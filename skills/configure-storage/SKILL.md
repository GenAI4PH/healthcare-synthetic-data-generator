---
name: configure-storage
description: Configure local or cloud destinations without embedding secrets.
---

# configure-storage

Status: **planned**. This document establishes the skill contract; do not claim the capability is operational in Phase 1.

1. Determine OS and user intent; inspect existing configuration and actual CLI command availability.
2. Present operations requiring permissions (download/install/network/upload/public GitHub posts) and obtain explicit approval.
3. Use the supported `hsg` CLI implementation when available; do not invent commands.
4. Validate actual outcomes, log the upstream version used, and report any blockers clearly.
5. Never commit synthetic records, secret credentials, or the upstream Synthea installation.
