# Healthcare Synthetic Data Generator

[![CI](https://github.com/GenAI4PH/healthcare-synthetic-data-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/GenAI4PH/healthcare-synthetic-data-generator/actions/workflows/ci.yml)

**Tell your AI coding agent what synthetic healthcare data you need. It can set up Synthea, configure the generator, run batches across US states, and produce ready-to-use files in your workspace.**

This agent-friendly Python CLI orchestrates the [official Synthea simulator](https://github.com/synthetichealth/synthea) to generate **CSV, FHIR R4 Bundle JSON, and C-CDA XML**. It supports one state or all 50 US states, checkpointed batch runs, CSV consolidation, local storage, and Amazon S3 delivery.

## AI-agent quick start — describe the dataset, not the commands

Open this repository in an AI coding agent such as ChatGPT Codex or a VS Code coding agent. Give it access to **your local clone or authorized sandbox**, allow it to read the repository's [`AGENTS.md`](AGENTS.md) and [`skills/`](skills/), and provide this prompt:

> Configure this repository to use the official pinned Synthea engine. Check prerequisites and install any missing dependencies with my approval. Generate **CSV** data for **10,000 requested living patients**, distributed across **all 50 US states**, in batches of **500 patients**. Merge CSV outputs into one header-preserving file per dataset type. Show me a preview of the plan, required permissions, disk usage considerations, and expected output location **before** running any installation or generation. After I approve, execute the workflow, validate the run manifest and files, and give me the resulting paths. Do not commit generated datasets or credentials.

Change the format (`csv`, `fhir`, or `ccda`), patient target, states, batch size, seed, and destination to match your needs. For example, ask for *1,000 FHIR R4 patients in New Jersey*, or *100 living patients per state with a batch size of 25*.

**What the agent can automate:**

1. Inspect the environment and repository instructions; check Python, Git, and a compatible JDK (JDK 17 recommended).
2. Download and verify the **pinned, unmodified upstream Synthea** source in an ignored local directory.
3. Preview generation settings for formats, patient targets, states, and batches.
4. Run approved generation commands, resume interrupted batches, and merge CSVs when requested.
5. Inspect the completed `manifest.json` and generated files, then optionally preview and upload to a private S3 bucket with separate approval.

**Required access and approvals:** The agent must have permission to run commands, read/write its designated workspace or sandbox, and reach the network for setup. Repository access alone does **not** give an agent access to your computer, cloud account, or shell. You must grant those permissions in your agent environment. This project's CLI deliberately uses explicit `--approve` flags for operations with side effects; the agent should show the plan and obtain your approval before executing them. AWS uploads also require independently configured credentials and authorization.

### Example agent-generated commands

```powershell
# Preview a 50-state CSV workload (1,000 requested living patients total)
hsg generate-batch csv --patients 1000 --all-states --allocation total --batch-size 100

# Execute after reviewing and approving the plan
hsg generate-batch csv --patients 1000 --all-states --allocation total --batch-size 100 --merge-csv --approve

# Generate a single-state FHIR R4 dataset
hsg generate fhir --patients 100 --state NJ --approve

# Generate 100 requested living patients per state (5,000 total)
hsg generate-batch csv --patients 100 --all-states --allocation per-state --batch-size 25 --approve
```

`--patients` specifies Synthea's **target living population**, not an exact number of exported patient rows. The agent should report actual output counts from run manifests rather than promise exact counts.

## Manual quick start (Windows PowerShell)

Prerequisites: Python 3.11+, Git and JDK 17.

```powershell
git clone https://github.com/GenAI4PH/healthcare-synthetic-data-generator.git
cd healthcare-synthetic-data-generator
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev,aws]'
$env:HSG_JAVA_HOME = 'C:\Program Files\Java\jdk-17'  # adjust to your JDK installation
hsg doctor
hsg setup-synthea
hsg setup-synthea --approve
hsg verify-synthea --approve
hsg generate csv --patients 10 --state NJ
hsg generate csv --patients 10 --state NJ --approve
```

On Linux/macOS use `python3 -m venv .venv`, `source .venv/bin/activate`, and set `HSG_JAVA_HOME` when needed. Approved runs are created under `output/runs/<format>/<run-id>/` with a `manifest.json`.

## Documentation

- [Setup](docs/setup.md) — prerequisites, installation and verification
- [Configuration](docs/configuration.md) — states, formats, seeds, output paths and S3
- [Usage Guide](docs/usage-guide.md) — single runs, batching, resume, merging and upload
- [Troubleshooting](docs/troubleshooting.md) — Java, paths, failed runs, permissions and CI

For agent instructions see [AGENTS.md](AGENTS.md) and [`skills/`](skills/). For contributions and project information see [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [CHANGELOG.md](CHANGELOG.md).

## Safety and limitations

Synthea is installed separately at a pinned revision; it is not bundled, modified, or redistributed here. This orchestration toolkit is Apache-2.0 licensed; see [third-party notices](THIRD_PARTY_NOTICES.md).

CSV merge does not deduplicate identifiers or guarantee foreign-key integrity. Output validation checks basic structure, not comprehensive FHIR/C-CDA conformance or clinical-data integrity. Remote S3 checksum verification and reliable partial-upload recovery are not implemented; Azure Blob and Google Drive adapters are experimental and unverified. These datasets are for synthetic development and testing, **not clinical care**.

Never commit generated files (`output/`), the upstream checkout (`external/`), or credentials. Review [SECURITY.md](SECURITY.md) for vulnerability reporting.
