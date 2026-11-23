"""Explicit pooling choices; none makes different model spaces comparable."""

from dataclasses import dataclass

import numpy as np

from free_foundations.encoders.contracts import FloatArray, Tokens


@dataclass(frozen=True)
class MeanPooling:
    """Average valid tokens; only meaningful when their channels are aligned."""

    name: str = "mean"

    def __call__(self, tokens: Tokens) -> FloatArray:
        """Ignore masked padding, including non-finite padding values."""
        mask = np.asarray(tokens.mask, dtype=np.bool_)
        selected = np.where(mask[..., None], tokens.values, 0.0)
        return selected.sum(axis=1) / mask.sum(axis=1, keepdims=True)


@dataclass(frozen=True)
class ConcatenatePooling:
    """Preserve ordered token coordinates, especially separate ensemble members."""

    name: str = "concatenate"

    def __call__(self, tokens: Tokens) -> FloatArray:
        """Concatenate only a complete fixed token layout."""
        if not np.asarray(tokens.mask).all():
            msg = "concatenation requires an unmasked, fixed token layout"
            raise ValueError(msg)
        return tokens.values.reshape(tokens.values.shape[0], -1)


@dataclass(frozen=True)
class SelectToken:
    """Select an explicitly identified summary token or ensemble member."""

    index: int = 0

    @property
    def name(self) -> str:
        """Record the selected index, not an assumed CLS-token interpretation."""
        return f"token:{self.index}"

    def __call__(self, tokens: Tokens) -> FloatArray:
        """Require the chosen token to exist and be valid for every row."""
        if not 0 <= self.index < tokens.values.shape[1]:
            msg = "selected token is outside the token axis"
            raise ValueError(msg)
        if not np.asarray(tokens.mask)[:, self.index].all():
            msg = "selected token is masked for at least one row"
            raise ValueError(msg)
        return tokens.values[:, self.index, :]
