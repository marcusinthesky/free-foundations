"""Optional checkpoint integration checks, run explicitly before the financial experiment."""

import os
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from free_foundations.representations import foundations
from free_foundations.representations.encoding import Prepared
from free_foundations.representations.setup import local_checkpoint

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_FOUNDATION_INTEGRATION") != "1",
    reason="Set RUN_FOUNDATION_INTEGRATION=1 with the pinned model extras and weights.",
)


@pytest.mark.parametrize("name", ["kumo", "limix"])
def test_native_head_fidelity_frozen_weights_and_batch_consistency(
    name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import torch  # noqa: PLC0415 -- optional model extra.

    torch.set_num_threads(2)
    cache = (
        next(p for p in Path(__file__).resolve().parents if (p / "dvc.yaml").is_file())
        / "research/expanded/cache"
    )
    metadata = local_checkpoint(cache, name)
    path = str(Path(metadata["root"]) / metadata["files"][0])
    model = foundations.load_kumo(path) if name == "kumo" else foundations.load_limix(path)
    assert not model.training
    assert all(not p.requires_grad for p in model.parameters())
    versions = [p._version for p in model.parameters()]  # noqa: SLF001 -- mutation audit.

    def loaded(*_args: object) -> Any:  # noqa: ANN401 -- upstream model.
        return model

    monkeypatch.setattr(foundations, f"load_{name}", loaded)
    rng = np.random.default_rng(42)
    data = Prepared(
        rng.normal(size=(32, 15)),
        rng.normal(size=(6, 15)),
        rng.normal(size=32),
        tuple(f"X{i}" for i in range(15)),
        tuple(f"S{i}" for i in range(32)),
        tuple(f"Q{i}" for i in range(6)),
        2020,
        "integration-audit-v1",
    )
    head = model.icl_block.head if name == "kumo" else model.reg_y_decoder
    observed: list[torch.Tensor] = []

    def observe(
        _module: torch.nn.Module, _args: tuple[torch.Tensor, ...], output: torch.Tensor
    ) -> None:
        observed.append(output.clone())

    handle = head.register_forward_hook(observe)
    whole = foundations.states(data, path, metadata["revision"], name, batch_size=6)
    handle.remove()
    assert len(observed) == 1
    with torch.inference_mode():
        reconstructed = head(
            torch.tensor(
                whole["late"], dtype=torch.float32, device=next(model.parameters()).device
            )[None]
        )
    torch.testing.assert_close(reconstructed.reshape_as(observed[0]), observed[0])
    split = foundations.states(data, path, metadata["revision"], name, batch_size=2)
    for key, values in whole.items():
        assert values.shape == (6, 1024)
        assert np.isfinite(values).all()
        np.testing.assert_allclose(values, split[key], atol=2e-5, rtol=2e-5)
    assert versions == [p._version for p in model.parameters()]  # noqa: SLF001
