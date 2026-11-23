#!/usr/bin/env bash
# Run from the repository root inside devenv after just latex::setup.
set -euo pipefail
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
section="$scratch/test section.tex"
cat > "$section" <<'TEX'
% REVIEW: for various reasons.
A comparison,
  highlighting its importance.
\label{for various reasons}\citet{for various reasons}\ffnum[2]{for various reasons}
\begin{table}
\begin{tabular}{l}for various reasons\end{tabular}
\caption{A table for various reasons.}
\end{table}

\begin{proposition}
The result follows naturally from the assumption.
\end{proposition}

The parser reads.
The lexer writes.
\[ \text{for various reasons} \]
\input{generated/tables/for various reasons}
TEX
cp "$section" "$scratch/original"
cat > "$scratch/expected" <<EXPECTED
$section:11:12: Manuscript.OrganicConsequence: follows naturally from
$section:14:1: Manuscript.ParallelStaccato: The parser reads. The lexer writes.
$section:3:3: Manuscript.ParticipialPadding: highlighting its importance
$section:7:18: Manuscript.VagueReasons: for various reasons
Reviewed 1 section(s), 4 advisory match(es).
EXPECTED
just latex::prose-lint "$section" | LC_ALL=C sort > "$scratch/actual"
diff -u "$scratch/expected" "$scratch/actual"
cmp "$section" "$scratch/original"

printf '%s\n' 'A broken citation \citet{unfinished' > "$section"
if just latex::prose-lint "$section" > "$scratch/error" 2>&1; then
  echo 'Malformed input unexpectedly passed' >&2
  exit 1
fi
rg -q 'LaTeX extraction failed' "$scratch/error"
