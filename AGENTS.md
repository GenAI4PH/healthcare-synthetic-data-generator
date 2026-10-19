# Agent instructions

Scope: This repository orchestrates official Synthea; do not vendor, fork, edit, or redistribute the Synthea engine by default.

1. Inspect relevant `skills/*/SKILL.md` before performing a user task. They are cross-agent Markdown skills; different agent products may require registration or adaptation.
2. Explain intended filesystem, network, package-install, and cloud effects; request approval before side effects.
3. Prefer `hsg` CLI calls over ad hoc execution or manual modification of the upstream Synthea installation.
4. Pin the Synthea revision and record its source URL/version. Do not rely on a mutable latest release for reproducible runs.
5. Keep downloaded upstream files, generated patient data, credentials, and logs containing secrets out of git.
6. After changes, run `python -m pytest` and report results; never claim generation/upload success without verification.
7. Do not post feedback, reviews, stars, or comments without the user's explicit final approval. Draft only factual feedback based on observed outcomes.
