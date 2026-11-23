---
description: One shared manuscript with arXiv and FinFM publishing adapters.
---

# Manuscript build

The paper project owns its sections, metadata, bibliography and generated result
fragments. `body.tex` and `appendix.tex` are the composition interfaces consumed
by both targets. Section files contain manuscript content and shared semantic
commands; classes, packages, title blocks and bibliography styles belong to the
target adapters. `templates/ff-manuscript.sty` holds the small shared vocabulary
for theorem environments and generated values.

The dependency direction is saved research artifacts to the one `publication`
renderer, then project-local `generated/` fragments, then target PDFs. The
renderer reads saved panel, replication, co-movement, alignment and APT outputs;
it does not estimate or acquire data. Its `quarterly-` and `apt-` value keys avoid
collisions. A source-only build displays a notice and placeholders. When a
catalogue exists, an unknown key fails the build. Manuscript authors
choose where to include table fragments and figures. The claims audit and DVC
stage make their numerical source traceable.

The arXiv target compiles with Tectonic's pinned asset bundle and the FinFM target
with the AAAI-27 author kit and pdfLaTeX. Their build outputs live in distinct
ignored `build/<target>/` directories. Target adapters may differ in layout and
front matter, while the body and appendix remain shared. `just latex::check`
builds both.

CSL reference records are canonical. `just sync` exports their BibTeX catalog
into the paper project. Lean declaration checks scan authored paper sections and
the blueprint, so moving or adding a formal result cannot bypass the proof
contract check. No generated Insitu region is edited as part of manuscript work.
