"""Download the unmodified upstream Synthea source at a pinned git revision."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Callable

import yaml

OFFICIAL_REPO = "https://github.com/synthetichealth/synthea.git"


class SetupError(RuntimeError):
    pass


def load_settings(config_path: Path) -> tuple[Path, str]:
    config_path = config_path.resolve()
    if not config_path.is_file():
        raise SetupError(f"Configuration not found: {config_path}")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    cfg = data.get("synthea") or {}
    url = cfg.get("source_repo", OFFICIAL_REPO)
    if url != OFFICIAL_REPO:
        raise SetupError("Only the official Synthea Git repository is supported")
    directory = Path(cfg.get("install_dir") or "external/synthea")
    if not directory.is_absolute():
        directory = config_path.parent.parent / directory
    version = cfg.get("version")
    if not isinstance(version, str) or not version.strip():
        raise SetupError("Set synthea.version to a reviewed upstream tag or commit in config/generator.yaml")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,127}", version) or version.startswith("-"):
        raise SetupError("Invalid Synthea git tag/commit format")
    return directory.resolve(), version


def run_command(args: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    if proc.returncode:
        raise SetupError(f"Command failed: {args[0]} (exit {proc.returncode})\n{proc.stderr[-1200:]}")
    return proc.stdout.strip()


def check_prerequisites() -> dict[str, str]:
    found: dict[str, str] = {}
    for binary in ("git", "java"):
        path = shutil.which(binary)
        if not path:
            raise SetupError(f"Missing prerequisite: {binary}. Install it separately with your approval")
        found[binary] = path
    java_details = subprocess.run(["java", "-version"], capture_output=True, text=True, check=False)
    if java_details.returncode:
        raise SetupError("java -version failed")
    version_line = (java_details.stderr or java_details.stdout).splitlines()[0]
    match = re.search(r'"(\d+)(?:\.(\d+))?', version_line)
    if not match:
        raise SetupError(f"Could not identify Java version: {version_line}")
    major = int(match.group(1))
    if major == 1:
        major = int(match.group(2) or 0)
    if major < 17:
        raise SetupError(f"Java 17+ required for this setup; found Java {major}")
    found["java_version"] = version_line
    return found


def install(config_path: Path, *, approved: bool = False) -> dict[str, str]:
    target, revision = load_settings(config_path)
    check_prerequisites()
    if target.exists():
        if not (target / ".git").is_dir():
            raise SetupError(f"Target exists and is not a git checkout: {target}")
        remote = run_command(["git", "remote", "get-url", "origin"], cwd=target)
        if remote != OFFICIAL_REPO:
            raise SetupError(f"Existing installation has unexpected origin: {remote}")
        if run_command(["git", "status", "--porcelain"], cwd=target):
            raise SetupError("Existing upstream checkout has changes; refusing to overwrite")
    if not approved:
        raise SetupError(f"Approval required to download/update {OFFICIAL_REPO} to {target}")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        run_command(["git", "clone", OFFICIAL_REPO, str(target)])
    run_command(["git", "fetch", "--tags", "origin"], cwd=target)
    # Only allow a release tag or a complete immutable commit SHA; disallow mutable branches.
    is_sha = bool(re.fullmatch(r"[a-fA-F0-9]{40}", revision))
    if not is_sha:
        tag = run_command(["git", "tag", "--list", revision], cwd=target)
        if revision not in tag.splitlines():
            raise SetupError(f"Pinned Synthea tag not found: {revision}")
    commit = run_command(["git", "rev-parse", "--verify", f"{revision}^{{commit}}"], cwd=target)
    run_command(["git", "checkout", "--detach", commit], cwd=target)
    manifest = {"repository": OFFICIAL_REPO, "requested_revision": revision, "commit": commit, "directory": str(target)}
    (target.parent / "synthea-install.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
