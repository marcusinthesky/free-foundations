"""Replace source outputs without writing through immutable DVC cache file links."""

from __future__ import annotations

import fcntl
import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    import pandas as pd


@contextmanager
def atomic_output(destination: Path) -> Iterator[Path]:
    """Write a fresh sibling inode, then replace only the destination directory entry."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=destination.parent, prefix=f".{destination.name}.", suffix=".partial", delete=False
    ) as stream:
        temporary = Path(stream.name)
    try:
        yield temporary
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_bytes(destination: Path, content: bytes) -> None:
    """Store exact bytes while preserving any old linked cache object."""
    with atomic_output(destination) as temporary:
        temporary.write_bytes(content)


def atomic_copy(destination: Path, source: Path) -> None:
    """Copy source bytes to a new inode before replacing a destination link."""
    with atomic_output(destination) as temporary:
        shutil.copy2(source, temporary)


def atomic_csv(destination: Path, frame: pd.DataFrame) -> None:
    """Materialize one complete CSV before replacing an earlier source output."""
    with atomic_output(destination) as temporary:
        frame.to_csv(temporary, index=False)


def atomic_parquet(destination: Path, frame: pd.DataFrame) -> None:
    """Materialize one complete parquet file before replacing an earlier source output."""
    with atomic_output(destination) as temporary:
        frame.to_parquet(temporary, index=False)


@contextmanager
def sources_lock(output: Path, *, exclusive: bool) -> Iterator[None]:
    """Coordinate source writers, complete preparation reads and snapshot promotion."""
    output.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output / ".sources.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "rb") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)
