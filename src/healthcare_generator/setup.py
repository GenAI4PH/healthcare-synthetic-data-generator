"""Download the unmodified upstream Synthea source at a pinned git revision."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import platform
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


def windows_path_warning(target: Path) -> str | None:
    """Warn before a Windows checkout likely to exceed legacy path limits."""
    if platform.system() != "Windows":
        return None
    # Upstream has nested test fixture filenames exceeding 150 characters.
    if len(str(target.resolve())) > 75:
        return (f"Windows installation path is long ({len(str(target.resolve()))} chars): {target}. "
                "Consider C:/synthea. Git long-path support is enabled for cloning, "
                "but other Windows tools may still have path limits.")
    return None


def java_runtime_major(output: str) -> int:
    match = re.search(r'(?:version\s+)?["\s](1\.)?(\d+)(?:[.\-+"\s]|$)', output)
    if not match:
        raise SetupError(f"Unable to parse Java version: {output[:120]}")
    return int(match.group(2))


def java_environment() -> dict[str, str]:
    """Validate both the shell JVM and the JVM Gradle will choose via JAVA_HOME."""
    jhome = os.environ.get("JAVA_HOME")
    if jhome:
        candidate = Path(jhome) / 'bin' / ('java.exe' if platform.system() == 'Windows' else 'java')
        if not candidate.is_file():
            raise SetupError(f"JAVA_HOME does not contain a Java executable: {candidate}")
        java_bin = str(candidate)
    else:
        java_bin = shutil.which('java')
        if not java_bin:
            raise SetupError('Java not found. Install JDK 17 and configure JAVA_HOME.')
    proc = subprocess.run([java_bin, '-version'], capture_output=True, text=True, check=False)
    if proc.returncode:
        raise SetupError(f'Java version check failed: {java_bin}')
    line = (proc.stderr or proc.stdout).splitlines()[0]
    major = java_runtime_major(line)
    # The upstream v4.0.0 Gradle 9.2.1 wrapper cannot run on Java 26.
    if not 17 <= major <= 25:
        raise SetupError(f'Java {major} is incompatible with the pinned Gradle 9.2.1 runtime; '
                         'use JDK 17 (recommended) through JAVA_HOME.')
    javac = Path(java_bin).with_name('javac.exe' if platform.system() == 'Windows' else 'javac')
    if not javac.is_file() and not shutil.which('javac'):
        raise SetupError('JDK required: javac not found. Install JDK 17 rather than a JRE.')
    return {'java': java_bin, 'java_version': line, 'java_major': str(major)}


def check_prerequisites() -> dict[str, str]:
    git = shutil.which('git')
    if not git:
        raise SetupError('Git not found in PATH')
    return {'git': git, **java_environment()}


def install(config_path: Path, *, approved: bool = False) -> dict[str, str]:
    target, revision = load_settings(config_path)
    check_prerequisites()
    warning = windows_path_warning(target)
    if warning:
        print(f"WARNING: {warning}")
    if target.exists():
        if not (target / ".git").is_dir():
            raise SetupError(f"Target exists and is not a git checkout: {target}")
        remote = run_command(["git", "remote", "get-url", "origin"], cwd=target)
        if remote != OFFICIAL_REPO:
            raise SetupError(f"Existing installation has unexpected origin: {remote}")
        if run_command(["git", "status", "--porcelain"], cwd=target):
            raise SetupError("Existing upstream checkout has changes or is incomplete. "
                             "Back up any changes, then manually remove or repair the Synthea checkout; "
                             "this tool will not delete it automatically")
    if not approved:
        raise SetupError(f"Approval required to download/update {OFFICIAL_REPO} to {target}")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        run_command(["git", "-c", "core.longpaths=true", "clone", OFFICIAL_REPO, str(target)])
    run_command(["git", "fetch", "--tags", "origin"], cwd=target)
    # Only allow a release tag or a complete immutable commit SHA; disallow mutable branches.
    is_sha = bool(re.fullmatch(r"[a-fA-F0-9]{40}", revision))
    if not is_sha:
        tag = run_command(["git", "tag", "--list", revision], cwd=target)
        if revision not in tag.splitlines():
            raise SetupError(f"Pinned Synthea tag not found: {revision}")
    commit = run_command(["git", "rev-parse", "--verify", f"{revision}^{{commit}}"], cwd=target)
    run_command(["git", "-c", "core.longpaths=true", "checkout", "--detach", commit], cwd=target)
    manifest = {"repository": OFFICIAL_REPO, "requested_revision": revision, "commit": commit, "directory": str(target)}
    (target.parent / "synthea-install.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
