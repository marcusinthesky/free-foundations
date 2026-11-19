set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments

mod python 'src/python/justfile'
mod lean 'src/lean/justfile'
mod latex 'src/latex/justfile'
mod agents '.agents/justfile'

workflow := "env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv run --offline --frozen --script src/python/scripts/workflow/script.py"

# Discover this project's commands.
default:
    @just --list

# Prepare locked dependencies and Git hooks (uses the network).
setup:
    env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv run --frozen --script src/python/scripts/workflow/script.py prepare
    just python::setup
    just lean::setup
    just latex::setup
    just agents::apply
    prek install

# Check source, views and selected languages without repairing files.
check:
    bash infra/nix/check.sh
    {{ workflow }} check
    just python::check
    just lean::check
    just latex::check
    just data-check
    just semflow-check
    just changelog-check
    just skills-check
    just agents::check

# Run the selected language tests.
test:
    just python::test
    just lean::test
    just latex::test

# Explicitly format sources.
fmt:
    git ls-files -z --cached --others --exclude-standard | while IFS= read -r -d '' file; do case "$file" in justfile|*/justfile) just --justfile "$file" --fmt --unstable ;; esac; done
    nixfmt devenv.nix infra/nix/devenv.nix infra/nix/pkgs/schematter.nix infra/nix/pkgs/lean-toolchain.nix infra/nix/pkgs/agentsync.nix
    tombi format --offline
    rumdl fmt .
    # DVC's YAML emitter can leave trailing spaces when wrapping scalar values.
    if [[ -f dvc.lock ]]; then sed -i 's/[[:blank:]]*$//' dvc.lock; fi
    just python::fmt
    just lean::fmt
    just latex::fmt

# Refresh generated planning and reference views.
sync:
    {{ workflow }} sync

# Validate document schemas, links and generated views.
context-check:
    {{ workflow }} check

# Create a plan without overwriting existing content.
plan-new slug title:
    {{ workflow }} plan-new "$1" --title "$2"

# Create a task inside an existing plan or task.
task-new parent slug title:
    {{ workflow }} task-new "$1" "$2" --title "$3"

# Create a citation record with its directory as citation key.
reference-new key title:
    {{ workflow }} reference-new "$1" --title "$2"

# Check external links online.
links:
    git ls-files -z '*.md' | xargs -0 -r lychee --config lychee.toml --no-progress

# Validate the repository changelog structure and change categories.
changelog-check:
    schematter validate --schema infra/schemas/documents/changelog.document-schema.yaml CHANGELOG.md

# Validate repository-owned skill documents and their directory names.
skills-check:
    git ls-files -z --cached --others --exclude-standard -- ':(glob)**/SKILL.md' 'SKILL.md' | while IFS= read -r -d '' file; do [[ -f "$file" ]] || continue; schematter validate --schema infra/schemas/documents/skill.document-schema.yaml "$file"; awk 'END { if (NR > 500) { print FILENAME ": exceeds 500 lines" > "/dev/stderr"; exit 1 } }' "$file"; env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv run --project src/python --offline --frozen python -c 'import pathlib, re, sys, yaml; p = pathlib.Path(sys.argv[1]); frontmatter = re.split(r"(?m)^---[ \t]*\r?$", p.read_text(), maxsplit=2)[1]; name = yaml.safe_load(frontmatter)["name"]; sys.exit(0 if name == p.parent.name else f"{p}: name {name!r} must match parent directory {p.parent.name!r}")' "$file"; done

# ── Data pipeline ──────────────────────────────────────────────────────────────
# Research runs are DVC stages (dvc.yaml): each reruns only when the code its command
# reaches (semflow fingerprint) or its inputs change, and is otherwise skipped.

# Run root-level DVC using the locked Python environment.
dvc *args:
    env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv run --project src/python --offline --frozen dvc "$@"

# Validate DVC metadata without fetching data.
data-check:
    just dvc status
    just dvc dag

# Check that semantic fingerprints match the code each DVC stage reaches.
semflow-check:
    env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv run --project src/python --offline --frozen --all-packages semflow check

# Preview the semantic dependency changes before applying them.
semflow-patch:
    env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv run --project src/python --offline --frozen --all-packages semflow patch

# Apply reviewed DVC and semantic fingerprint changes.
semflow-apply:
    env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv run --project src/python --offline --frozen --all-packages semflow patch --apply

# Refresh existing semantic fingerprints without editing the DVC graph.
semflow-refresh:
    env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv run --project src/python --offline --frozen --all-packages semflow refresh --apply

# Recheck code fingerprints, then rebuild every stale stage.
build: semflow-check
    just dvc repro

pipeline-graph:
    just dvc dag --mermaid

# The bucket is private: set S3 credentials in .dvc/config.local first (README).
data-pull *targets:
    just dvc pull "$@"

data-push:
    just dvc push

# Source acquisition is frozen so routine repros never refetch it. This recipe never
# executes the extraction script or accesses WRDS. EDGAR_IDENTITY can provide your SEC
# contact name and email.
stages := "env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv run --project src/python --offline --frozen --package free-foundations free-foundations"

# Stage SEC and factor recovery for a CRSP extract, promote it, and record the DVC stage.
sources crsp script:
    {{ stages }} raw acquire --crsp-csv "{{ crsp }}" --extraction-script "{{ script }}"
    {{ stages }} raw freeze
    just dvc commit -f raw_sources

# Each research stage reruns only when its inputs, parameters or code fingerprints change.
representations:
    just dvc repro processed_assemble_states

replication:
    just dvc repro research_collect_replication

comovement:
    just dvc repro research_estimate_comovement

alignment:
    just dvc repro research_measure_alignment

publication:
    just dvc repro publication_render

# Render saved study results for the manuscript without running DVC stages.
latex-assets:
    mkdir -p src/latex/build
    MPLCONFIGDIR="$PWD/src/latex/build/matplotlib" {{ stages }} publication render
