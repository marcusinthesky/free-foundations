#!/usr/bin/env bash
set -euo pipefail

project=$(realpath "$1")
src="$project/src"
out="$project/build/arxiv"
mkdir -p "$out"
work=$(mktemp -d "$out/.bundle-XXXXXXXX")
trap 'rm -rf "$work"' EXIT
mkdir "$work/src"
cd "$work/src"

cp -RL "$src/sections" "$src/generated" .
cp "$src"/{body.tex,appendix.tex,refs.bib} .
sed 's|{../../../templates/ff-manuscript}|{ff-manuscript}|' "$src/targets/arxiv.tex" > main.tex
sed '/^\\newcommand{\\papercontact}/d' "$src/metadata.tex" > metadata.tex
cp "$project/../../templates/ff-manuscript.sty" .
# Source-only builds permit missing exhibits. An upload must typeset each one.
printf '%s\n' '\renewcommand{\ffmissing}{\PackageError{ff-manuscript}{Missing publication exhibit}{Run just latex::assets.}}' >> ff-manuscript.sty

compile() {
  pdflatex -no-shell-escape -halt-on-error -interaction=nonstopmode -recorder main.tex \
    > /dev/null || { tail -40 main.log; exit 1; }
}
compile
bibtex main
compile

# The recorder includes dynamically selected tables as well as inline figures.
# Ship just the local inputs read by TeX, plus the BibTeX source.
{
  echo refs.bib
  awk '/^INPUT / {
    sub(/^INPUT /, ""); sub(/^\.\//, "")
    if ($0 !~ /^\// && ($0 ~ /\.(tex|sty|bbl)$/ || $0 ~ /^generated\/figures\/.*\.pdf$/)) print
  }' main.fls
} | LC_ALL=C sort -u > "$work/files"
tar --owner=0 --group=0 --mtime=@0 -czf "$work/arxiv.tar.gz" -T "$work/files"

mkdir "$work/verify"
cd "$work/verify"
tar -xzf "$work/arxiv.tar.gz"
compile
compile
if rg 'Citation.+undefined|Reference.+undefined|There were undefined|multiply[- ]defined|Rerun to get' main.log; then
  exit 1
fi
mv "$work/arxiv.tar.gz" "$out/arxiv.tar.gz"
echo "Wrote $out/arxiv.tar.gz"
