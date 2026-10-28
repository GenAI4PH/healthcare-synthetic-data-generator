# Set up the Healthcare Synthetic Data Generator on Windows, Linux, or macOS

This project is a Python CLI that **orchestrates** a separately installed, pinned official Synthea engine. Synthea itself runs on Java/Gradle; you do **not** need to install Gradle globally because the upstream checkout supplies its Gradle wrapper.

## Common prerequisites

- **Python 3.11 or newer** (tested in CI on 3.11 and 3.12; local Python 3.13 testing is also supported by the package constraints).
- **Git** on the terminal `PATH`.
- **JDK 17** (recommended; avoid Java 26 for the pinned upstream Gradle build).
- Internet access to clone Git repositories and download Gradle/Maven dependencies during initial setup.
- Sufficient free space for the Synthea source/build cache and the generated output; batch size, population and format affect storage and RAM usage.
- A POSIX-style shell for the Linux/macOS commands below, or PowerShell on Windows.

The official Synthea checkout is installed in an ignored directory (`external/` by default); no synthetic patient files should be checked into Git.

## Windows 10/11 (PowerShell)

1. Install Python 3.11+, Git for Windows, and JDK 17 from trusted vendor distributions. Confirm:

   ```powershell
   py -3 --version
   git --version
   & 'C:\Program Files\Java\jdk-17\bin\java.exe' -version
   ```

2. Clone, make a virtual environment, and install the CLI:

   ```powershell
   git clone https://github.com/GenAI4PH/healthcare-synthetic-data-generator.git
   cd healthcare-synthetic-data-generator
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -e '.[dev]'
   ```

   If PowerShell blocks activation, you can use `.\.venv\Scripts\python.exe -m pip ...` and `.\.venv\Scripts\hsg.exe ...` directly instead of changing execution policy.

3. Select JDK 17 for **this terminal only**, without changing your machine-wide Java installation:

   ```powershell
   $env:HSG_JAVA_HOME = 'C:\Program Files\Java\jdk-17'   # adjust to the actual folder
   hsg doctor
   ```

   If the checkout path is long, move it to a short directory. Git for Windows may require `git config --global core.longpaths true` when file paths exceed Windows limits.

## Ubuntu/Debian Linux (bash)

1. Install the required system packages. Package names and available Python versions vary by distribution:

   ```bash
   sudo apt update
   sudo apt install -y git python3 python3-venv python3-pip openjdk-17-jdk
   python3 --version
   git --version
   java -version
   ```

   **Check that `python3 --version` reports at least 3.11.** If your distribution's default Python is older, install Python 3.11+ through a supported distribution package or official Python distribution and use that binary explicitly. Other Linux distributions should use their package manager for the equivalent dependencies.

2. Clone and install into a local virtual environment:

   ```bash
   git clone https://github.com/GenAI4PH/healthcare-synthetic-data-generator.git
   cd healthcare-synthetic-data-generator
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -e '.[dev]'
   ```

3. Choose JDK 17 if multiple Java versions are installed:

   ```bash
   export HSG_JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")"
   "$HSG_JAVA_HOME/bin/java" -version
   hsg doctor
   ```

   The auto-detection line uses the active `javac` path; verify it points to **JDK 17**, or instead set `HSG_JAVA_HOME` explicitly (for example `/usr/lib/jvm/java-17-openjdk-amd64` on some x86_64 Ubuntu/Debian systems).

## macOS (Apple Silicon or Intel, zsh)

1. Install Git, Python 3.11+, and JDK 17. One option with [Homebrew](https://brew.sh/) already installed:

   ```bash
   brew install git python@3.12 openjdk@17
   ```

   Homebrew is optional. You may instead install Python and JDK 17 from their official distributions. On macOS, Homebrew's JDK is often **keg-only**; you can select it explicitly without modifying the global Java installation.

2. Clone the repository and create an environment with the intended Python binary:

   ```bash
   git clone https://github.com/GenAI4PH/healthcare-synthetic-data-generator.git
   cd healthcare-synthetic-data-generator
   "$(brew --prefix python@3.12)/bin/python3.12" -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -e '.[dev]'
   ```

   If you installed Python without Homebrew, replace the quoted Python path with your Python 3.11+ executable, e.g. `python3.12`.

3. Configure JDK 17 for the generator and verify it:

   ```bash
   export HSG_JAVA_HOME="$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home"
   "$HSG_JAVA_HOME/bin/java" -version
   hsg doctor
   ```

   For non-Homebrew JDKs, `/usr/libexec/java_home -v 17` can discover an installed registered JDK: `export HSG_JAVA_HOME="$(/usr/libexec/java_home -v 17)"`.

## Install and verify the pinned Synthea engine (all platforms)

Run the following **after** installing the CLI and choosing JDK 17:

```bash
hsg doctor
hsg setup-synthea                   # preview only
hsg setup-synthea --approve         # network download / checkout
hsg verify-synthea --approve        # runs Synthea smoke test
```

A successful verification creates smoke-test files under `output/smoke-test/`. Setup is only necessary once for a verified, pinned checkout. Do not modify the checked-out upstream source without updating the project's pin and its verification strategy.

## Generate and inspect a first sample (all platforms)

```bash
hsg generate csv --patients 10 --state NJ          # preview
hsg generate csv --patients 10 --state NJ --approve
hsg generate fhir --patients 10 --state NJ --approve
hsg generate ccda --patients 10 --state NJ --approve
```

Each approved command creates a unique `output/runs/<format>/<run-id>/` with a `manifest.json`. Check that the manifest reports `status: completed`; a failed run's files are not an approved complete dataset. For batch workflows, see the [usage guide](usage-guide.md).

## Optional AWS S3 delivery

```bash
python -m pip install -e '.[aws]'
hsg storage-plan 'output/runs/csv/<completed-run-id>' --provider s3
# Only after configuring AWS credentials, a private bucket and config/storage.yaml:
hsg upload 'output/runs/csv/<completed-run-id>' --provider s3 --approve
```

Use AWS SSO/roles, never hard-coded keys. The above syntax uses single quotes and works in bash/zsh and PowerShell. See [configuration](configuration.md) for storage settings.

## Troubleshooting checklist

- `hsg` not found: activate `.venv` or run the venv's `hsg` executable.
- Missing `venv`: install your Linux distribution's `python3-venv` package or use a full Python installer.
- Java/Gradle incompatibility: verify `"$HSG_JAVA_HOME/bin/java" -version` on Linux/macOS, or `& "$env:HSG_JAVA_HOME\bin\java.exe" -version` on PowerShell.
- `hsg doctor` fails: check Python/Git/JDK locations, network, and available space.
- Verification fails: review CLI output and [troubleshooting](troubleshooting.md); do not mark a failed run complete manually.
