"""Shared inference device selection, with an optional cap on this process's VRAM."""

import os


def inference_device() -> str:
    """Prefer CUDA; allow an explicit device override for reproducibility.

    ``FF_CUDA_MEMORY_FRACTION`` caps this process's share of GPU memory, so a shared
    GPU fails here with an out-of-memory error rather than starving another job.
    """
    import torch  # noqa: PLC0415 -- optional model runtime.

    device = os.environ.get("FF_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
    fraction = os.environ.get("FF_CUDA_MEMORY_FRACTION")
    if device.startswith("cuda") and fraction:
        torch.cuda.set_per_process_memory_fraction(float(fraction))
    return device
