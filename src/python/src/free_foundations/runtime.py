"""Shared inference device selection without imposing CPU thread or memory limits."""

import os


def inference_device() -> str:
    """Prefer CUDA; allow an explicit device override for reproducibility."""
    import torch  # noqa: PLC0415 -- optional model runtime.

    return os.environ.get("FF_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
