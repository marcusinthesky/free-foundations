"""Contract properties that protect alignment and point-in-time measurements."""

from dataclasses import replace
from datetime import timedelta
from typing import Literal

import numpy as np
import pytest
from hypothesis import given
from numpy.testing import assert_allclose, assert_array_equal

from free_foundations import (
    MODELS,
    ConcatenatePooling,
    Context,
    MeanPooling,
    SelectToken,
    TabularEncoder,
    Tokens,
    from_fitted,
    model_spec,
)
from free_foundations.contracts import Encoder, FloatArray, PanelBatch
from tests.strategies import CUTOFF, panel, token_arrays, tokens


class FixedReadout:
    def __init__(self, value: Tokens) -> None:
        self.value = value
        self.calls = 0

    def __call__(self, batch: PanelBatch) -> Tokens:
        self.calls += 1
        assert len(batch.row_ids) == self.value.values.shape[0]
        return self.value


def encoder(readout: FixedReadout) -> TabularEncoder:
    return TabularEncoder(
        model="exaone",
        extract=readout,
        feature_names=("assets", "debt"),
        checkpoint="test-revision",
        readout="test-hidden-state",
        preprocessing="identity-v1",
    )


@given(tokens())
def test_pooling_preserves_rows_and_permutation(value: Tokens) -> None:
    reversed_tokens = Tokens(value.values[::-1])
    for pooling in (MeanPooling(), ConcatenatePooling(), SelectToken()):
        actual = pooling(value)
        assert actual.shape[0] == value.values.shape[0]
        assert_allclose(pooling(reversed_tokens), actual[::-1])
    assert_array_equal(ConcatenatePooling()(value).reshape(value.values.shape), value.values)
    assert_allclose(MeanPooling()(value), value.values.mean(axis=1))
    assert_array_equal(SelectToken()(value), value.values[:, 0, :])


@given(token_arrays())
def test_masked_padding_never_changes_mean(values: FloatArray) -> None:
    rows, _, width = values.shape
    padded = np.concatenate((values, np.full((rows, 2, width), np.nan)), axis=1)
    mask = np.ones(padded.shape[:2], dtype=np.bool_)
    mask[:, -2:] = False
    value = Tokens(padded, mask)
    assert_allclose(MeanPooling()(value), values.mean(axis=1))
    with pytest.raises(ValueError, match="unmasked"):
        ConcatenatePooling()(value)
    with pytest.raises(ValueError, match="masked"):
        SelectToken(value.values.shape[1] - 1)(value)


@given(tokens())
def test_result_preserves_identity_and_owns_its_values(value: Tokens) -> None:
    readout = FixedReadout(value)
    backend: Encoder = encoder(readout)
    batch = panel(value.values.shape[0])
    result = backend.encode(batch)
    assert result.row_ids == batch.row_ids
    assert result.as_of == batch.as_of
    assert result.provenance.pooling == "concatenate"
    assert result.provenance.checkpoint == "test-revision"
    assert not result.values.flags.writeable
    assert not batch.values.flags.writeable
    assert not np.shares_memory(result.values, value.values)
    assert readout.calls == 1


@pytest.mark.parametrize("violation", ["future", "overlap", "schema"])
def test_invalid_context_fails_before_inference(violation: str) -> None:
    batch = panel(2)
    readout = FixedReadout(Tokens(np.ones((2, 1, 3))))
    context = Context("support-v1", CUTOFF, ("other-observation",))
    if violation == "future":
        context = replace(context, available_at=CUTOFF + timedelta(seconds=1))
    elif violation == "overlap":
        context = replace(context, row_ids=(batch.row_ids[0],))
    else:
        batch = replace(batch, feature_names=tuple(reversed(batch.feature_names)))
    with pytest.raises(ValueError, match=r"context|schema"):
        replace(encoder(readout), context=context).encode(batch)
    assert readout.calls == 0


class NativeBackend:
    def __init__(self, values: FloatArray) -> None:
        self.values = values

    def get_embeddings(
        self,
        features: FloatArray,
        /,
        *,
        data_source: Literal["test"] = "test",
    ) -> FloatArray:
        assert features.shape[0] == self.values.shape[1]
        assert data_source == "test"
        # Reproduce the singleton query squeeze in TabPFN's public method.
        return self.values[:, 0, :] if features.shape[0] == 1 else self.values


@given(token_arrays())
def test_native_ensemble_conversion_never_interleaves_rows(values: FloatArray) -> None:
    backend = NativeBackend(values.transpose(1, 0, 2))
    batch = panel(values.shape[0])
    wrapped = from_fitted(
        "tabpfn",
        backend,
        feature_names=batch.feature_names,
        checkpoint="test-sha",
        preprocessing="fixed-v1",
        context=Context("context-v1", CUTOFF, ("support",)),
    )
    assert_array_equal(wrapped.encode(batch).values, values.reshape(values.shape[0], -1))


def test_registry_is_complete_and_unsupported_extraction_is_explicit() -> None:
    assert set(MODELS) == {"exaone", "tabpfn", "limix", "causilo", "tabfm", "sap"}
    assert model_spec("tabfm").url.endswith("google/tabfm-1.1.0-pytorch")
    with pytest.raises(ValueError, match="Unknown model"):
        model_spec("typo")
    for deferred in ("nori", "tabldm"):
        with pytest.raises(ValueError, match="Unknown model"):
            model_spec(deferred)
    with pytest.raises(NotImplementedError, match="explicit readout"):
        from_fitted(
            "causilo",
            NativeBackend(np.ones((1, 1, 1))),
            feature_names=("assets",),
            checkpoint="sha",
            preprocessing="v1",
            context=Context("support", CUTOFF, ("context-row",)),
        )


def test_invalid_tensors_and_zero_norms_fail_loudly() -> None:
    with pytest.raises(ValueError, match="valid token"):
        Tokens(np.full((1, 1, 2), np.nan))
    with pytest.raises(ValueError, match="at least one"):
        Tokens(np.ones((1, 1, 2)), np.zeros((1, 1), dtype=np.bool_))
    with pytest.raises(ValueError, match="zero vector"):
        replace(encoder(FixedReadout(Tokens(np.zeros((1, 1, 2))))), normalize=True).encode(panel(1))
    result = replace(encoder(FixedReadout(Tokens(np.ones((1, 1, 2))))), normalize=True).encode(
        panel(1)
    )
    assert_allclose(np.linalg.norm(result.values, axis=1), 1.0)
    assert result.provenance.normalized
