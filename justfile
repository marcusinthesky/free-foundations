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

# Reject proof gaps and nonstandard axioms, including unused private declarations.
lean-audit: lean-build
    cd src/lean && lake env lean Audit.lean

# Saved-artifact rendering only; no empirical estimation.
latex-assets:
    mkdir -p src/latex/build
    MPLCONFIGDIR="$PWD/src/latex/build/matplotlib" uv run --project src/python --frozen python src/latex/render_results.py

latex-build: latex-assets
    mkdir -p src/latex/build
    tectonic --keep-logs -o src/latex/build src/latex/main.tex

# Main text, abstract and captions; TeXcount directives exclude the supplement.
latex-count: latex-assets
    cd src/latex && texcount -merge -sub=section main.tex > build/word-count.txt
    cat src/latex/build/word-count.txt

# Lean blueprint (leanblueprint/plasTeX). The Lean project is src/lean, not the git root,
# so these recipes run the leanblueprint CLI's steps directly.
blueprint-web:
    cd src/lean/blueprint/src && uv run --frozen plastex -c plastex.cfg web.tex

blueprint-pdf:
    mkdir -p src/lean/blueprint/print
    tectonic -o src/lean/blueprint/print src/lean/blueprint/src/print.tex

# Every \lean{...} name in the blueprint and the manuscript must be a compiled declaration.
blueprint-check: blueprint-web lean-build
    python3 src/lean/blueprint/manuscript_decls.py src/latex/main.tex > src/lean/blueprint/manuscript_decls
    cd src/lean && lake exe checkdecls blueprint/lean_decls && lake exe checkdecls blueprint/manuscript_decls

blueprint-serve:
    cd src/lean/blueprint/web && python -m http.server 8000

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

# Research runs are DVC stages (dvc.yaml): each reruns only when the code its command
# reaches (semflow fingerprint) or its inputs change, and is otherwise skipped.
# The network-acquisition stages are frozen so routine repros never refetch them. These
# recipes resume one deliberately: unprotect its linked cache, run the stage's command,
# then record the result. EDGAR_IDENTITY must contain your name and email.
python-universe:
    dvc unprotect research/universe/cache
    uv run --project src/python --frozen free-foundations universe run
    dvc commit -f universe

# The paper has one declared study; preparation and model extraction are cached separately.
python-panel:
    dvc repro measurement

python-representations:
    dvc repro representations

# The supporting CAPM replication and VaR audit do not load foundation models.
python-fernandez:
    dvc repro replication

python-publication:
    dvc repro publication

# Recheck code fingerprints, then rebuild every stale stage.
build:
    uv run --project src/python --frozen semflow check
    dvc repro

# Refresh fingerprints after a code change; patch first if dvc.yaml's commands changed.
semflow-refresh:
    uv run --project src/python --frozen semflow refresh --apply

pipeline-graph:
    dvc dag --mermaid

# The bucket is private: set S3 credentials in .dvc/config.local first (README).
data-pull *targets:
    dvc pull {{ targets }}

data-push:
    dvc push
