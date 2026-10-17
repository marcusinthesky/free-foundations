set shell := ["bash", "-euc"]

default:
    @just --list

# Include untracked scaffold files as well as tracked source files.
check:
    git ls-files --cached --others --exclude-standard -z | xargs -0 -r prek run --files

fmt:
    nixfmt devenv.nix
    tombi format --offline
    rumdl fmt .
    uv run --project src/python --frozen ruff format src/python
    biome format --write src/typescript
    tex-fmt src/latex/main.tex

sync:
    uv sync --frozen
    uv sync --project src/python --frozen

insitu-check:
    uv run --frozen insitu check

insitu-sync:
    uv run --frozen insitu sync

lean-build:
    cd src/lean && lake build

latex-build:
    mkdir -p src/latex/build
    tectonic -o src/latex/build src/latex/main.tex

# Full verification; testmon is an explicit fast development loop below.
python-check:
    cd src/python && env -u PYTHONPATH uv run --frozen pyrefly check
    cd src/python && uv run --frozen tach check
    cd src/python && uv run --frozen vulture
    cd src/python && uv run --frozen pytest

python-testmon:
    cd src/python && uv run --frozen pytest --testmon

# Example: just python-model tabpfn
python-model model:
    uv sync --project src/python --frozen --extra {{ model }}

# EDGAR_IDENTITY must contain your name and email. All large inputs stay in cache/.
python-pilot:
    uv run --project src/python --frozen --extra tabpfn python -m free_foundations.pilot all --pretrained

# Reuse the original pilot data and run the expanded representation/metric grid.
python-expanded:
    OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 uv run --project src/python --frozen --extra tabpfn --extra tabfm --extra exaone python -m free_foundations.expanded.run
    uv run --project src/python --frozen python -m free_foundations.expanded.report

# Paper-aligned MM/IV/ML replication plus the matched-characteristic ladder.
python-fernandez:
    OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 TABPFN_DISABLE_TELEMETRY=1 uv run --project src/python --frozen --extra tabpfn --extra tabfm --extra exaone python -m free_foundations.fernandez.run
    OPENBLAS_NUM_THREADS=2 uv run --project src/python --frozen python -m free_foundations.fernandez.simulation
    uv run --project src/python --frozen python -m free_foundations.fernandez.report

# One spatial-error likelihood per combined network on a fixed common cohort.
python-fernandez-combined:
    OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 TABPFN_DISABLE_TELEMETRY=1 uv run --project src/python --frozen --extra tabpfn --extra tabfm --extra exaone python -m free_foundations.fernandez.combined

# Larger public-data universe, extended history, and an annual PIT coverage audit.
python-universe:
    uv run --project src/python --frozen python -m free_foundations.universe.run

# Shared annual cohorts; one 2016-2019 intensity per approach; 2020-2025 held out.
python-panel:
    OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 TABPFN_DISABLE_TELEMETRY=1 uv run --project src/python --frozen --extra tabpfn --extra tabfm --extra exaone python -m free_foundations.panel.run
    uv run --project src/python --frozen python -m free_foundations.panel.report
