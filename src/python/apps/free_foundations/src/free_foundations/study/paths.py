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
