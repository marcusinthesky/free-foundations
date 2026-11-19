"""Locations for the independent FinFM matched-comparison stages."""

from free_foundations.study.paths import CACHE, PROCESSED, PUBLICATION, RESULTS, WEIGHTS

MATCHED_PROCESSED = PROCESSED / "matched-comparisons"
MATCHED_CONTEXTS = MATCHED_PROCESSED / "contexts"
MATCHED_CELLS = MATCHED_PROCESSED / "cells"
MATCHED_RESULTS = RESULTS / "matched-comparisons"
MATCHED_PUBLICATION = PUBLICATION.with_name("finfm-matched")
MATCHED_CACHE = CACHE
MATCHED_WEIGHTS = WEIGHTS
