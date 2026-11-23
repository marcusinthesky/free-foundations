"""Device selection follows hardware availability and explicit overrides."""

import pytest

from free_foundations.encoders.runtime import inference_device


@pytest.mark.parametrize("available", [False, True])
def test_inference_device_prefers_cuda(monkeypatch: pytest.MonkeyPatch, *, available: bool) -> None:
    import torch  # noqa: PLC0415

    monkeypatch.delenv("FF_DEVICE", raising=False)
    monkeypatch.setattr(torch.cuda, "is_available", lambda: available)
    assert inference_device() == ("cuda" if available else "cpu")


def test_explicit_device_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FF_DEVICE", "cpu")
    assert inference_device() == "cpu"
