"""Frozen TabPFN query embeddings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from free_foundations.encoders.encoding import from_fitted
from free_foundations.encoders.runtime import inference_device

if TYPE_CHECKING:
    from free_foundations.encoders.contracts import FloatArray


from free_foundations.encoders.context import Prepared, provenance_context, query_batch


def tabpfn_states(
    data: Prepared,
    path: str,
    checkpoint: str,
) -> dict[str, FloatArray]:
    """Use the supported native query-embedding API with one ensemble member."""
    from tabpfn import TabPFNRegressor  # noqa: PLC0415
    from tabpfn.constants import ModelVersion  # noqa: PLC0415

    options: dict[str, Any] = {}
    if data.preprocessing.startswith("native-na"):
        from tabpfn.preprocessing.configs import PreprocessorConfig  # noqa: PLC0415

        # The wide-XBRL adapter partitions columns explicitly. Disable hidden column
        # expansion/subsampling so one member consumes the entire declared block.
        options["inference_config"] = {
            "PREPROCESS_TRANSFORMS": [
                PreprocessorConfig(
                    "none", append_original=False, max_features_per_estimator=len(data.features)
                )
            ],
            "FINGERPRINT_FEATURE": False,
            "POLYNOMIAL_FEATURES": "no",
            "FEATURE_SHIFT_METHOD": None,
            "SUBSAMPLE_SAMPLES": None,
            "OUTLIER_REMOVAL_STD": None,
            "REGRESSION_Y_PREPROCESS_TRANSFORMS": (None,),
        }
    model = TabPFNRegressor.create_default_for_version(
        ModelVersion.V3_5,
        model_path=path,
        n_estimators=1,
        device=inference_device(),
        random_state=42,
        **options,
    )
    model.fit(data.support, data.targets)
    encoder = from_fitted(
        "tabpfn",
        model,
        feature_names=data.features,
        checkpoint=checkpoint,
        preprocessing=f"{data.preprocessing}:{data.digest}",
        context=provenance_context(data),
    )
    result = encoder.encode(query_batch(data))
    return {"late": result.values}
