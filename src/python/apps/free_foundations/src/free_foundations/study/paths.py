"""Default artifact locations shared by the study CLI layers."""

from pathlib import Path

SOURCES = Path("data/raw/crsp-sec")
STAGING = Path("data/staging/crsp-sec")
WEIGHTS = Path("data/raw/models")
CACHE = Path("data/cache/crsp-sec/state-cache")
PROCESSED = Path("data/processed/crsp-sec")
PANEL = PROCESSED / "panel"
CONTEXTS = PROCESSED / "contexts"
PARTS = PROCESSED / "state-parts"
STATES = PROCESSED / "representations"
RESULTS = Path("data/research/crsp-sec/experiments")
PUBLICATION = Path("data/publication/crsp-sec/free-foundations")
MATCHED_PROCESSED = PROCESSED / "matched-comparisons"
MATCHED_CONTEXTS = MATCHED_PROCESSED / "contexts"
MATCHED_CELLS = MATCHED_PROCESSED / "cells"
MATCHED_RESULTS = RESULTS / "matched-comparisons"
MATCHED_PUBLICATION = PUBLICATION.with_name("finfm-matched")
