# Setup

## Requirements

- Python 3.11 or newer and Git.
- JDK 17 recommended (the pinned Synthea Gradle wrapper is incompatible with Java 26).
- Network connectivity and available disk space to clone and build official Synthea.
- On Windows, use a short checkout path and enable Git long paths if necessary (`git config --global core.longpaths true`).

## Install

```powershell
git clone https://github.com/GenAI4PH/healthcare-synthetic-data-generator.git
cd healthcare-synthetic-data-generator
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
$env:HSG_JAVA_HOME = 'C:\Program Files\Java\jdk-17' # adjust to installed JDK
hsg doctor
hsg setup-synthea                 # preview
hsg setup-synthea --approve       # downloads pinned official source
hsg verify-synthea --approve      # smoke test; uses Gradle
```

For macOS/Linux use `python3 -m venv .venv`, `source .venv/bin/activate` and configure `JAVA_HOME`/`HSG_JAVA_HOME` to your installed JDK. Use `hsg setup-synthea --help` for available options.

`hsg verify-synthea` runs official Synthea and writes to `output/smoke-test/`. If you already have a verified checkout, setup need not be repeated.
