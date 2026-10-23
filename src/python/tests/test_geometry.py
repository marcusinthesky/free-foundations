"""Independent covariance likelihood and principal-coordinate algebra checks."""

import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.stats import multivariate_normal

from free_foundations.fernandez.models import rank_distance
from free_foundations.panel.geometry import (
    THETA_MAX,
    block,
    chord_gram,
    covariance,
    fit,
    forecast_covariance,
    joint_gram,
    pcoa,
    rms_scales,
    unit_gram,
    validate_gram,
)


def test_rank_chords_recover_spearman_and_joint_average() -> None:
    histories = np.array([[1, 2, 3, 4], [4, 3, 2, 1], [2, 4, 1, 3]], dtype=float)
    first = chord_gram(rank_distance(histories))
    assert_allclose(first, [[1, -1, 0], [-1, 1, 0], [0, 0, 1]], atol=1e-14)
    second = unit_gram(np.array([[1, 2], [4, 1], [-1, -3]], dtype=float))
    joint = joint_gram([first, second])
    distance = np.sqrt(np.mean([2 * (1 - first), 2 * (1 - second)], axis=0))
    np.fill_diagonal(distance, 0)
    assert_allclose(joint, chord_gram(distance), atol=1e-14)
    assert joint[0, 1] < 0
    assert_allclose(np.diag(joint), 1)
    assert np.linalg.eigvalsh(joint)[0] > -1e-12


def test_unit_geometry_is_scale_rotation_and_permutation_equivariant() -> None:
    rng = np.random.default_rng(8)
    values = rng.normal(size=(9, 4))
    rotation, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    expected = unit_gram(values)
    assert_allclose(unit_gram((values @ rotation) * np.arange(1, 10)[:, None]), expected)
    # Finite vectors at extreme scales still have well-defined unit directions.
    assert_allclose(unit_gram(values * 1e300), expected, atol=1e-14)
    assert_allclose(unit_gram(values * 1e-300), expected, atol=1e-14)
    order = rng.permutation(len(values))
    assert_allclose(unit_gram(values[order]), expected[np.ix_(order, order)])


@pytest.mark.parametrize(
    "invalid",
    [np.eye(2) * 2, np.array([[1, 2], [2, 1]]), np.array([[1, 0], [0.1, 1]])],
)
def test_invalid_grams_are_rejected_without_repair(invalid: np.ndarray) -> None:
    with pytest.raises(ValueError, match="Gram matrix"):
        validate_gram(invalid)


def test_zero_vectors_and_non_chord_distances_are_rejected() -> None:
    with pytest.raises(ValueError, match="zero firm vectors"):
        unit_gram(np.array([[1, 2], [0, 0]], dtype=float))
    with pytest.raises(ValueError, match="negative eigenvalues"):
        chord_gram(2 * (np.ones((3, 3)) - np.eye(3)))
    with pytest.raises(ValueError, match="at least one"):
        joint_gram([])


def test_direct_covariance_preserves_marginals_and_signed_dependence() -> None:
    gram = unit_gram(np.array([[1, 0], [-1, 0], [0, 1]], dtype=float))
    scales = np.array([0.01, 0.02, 0.03])
    expected = np.outer(scales, scales) * ((1 - 0.7) * np.eye(3) + 0.7 * gram)
    result = covariance(gram, scales, 0.7)
    assert_allclose(result, expected)
    assert_allclose(result.diagonal(), scales**2)
    assert result[0, 1] < 0
    assert np.linalg.eigvalsh(result)[0] > 0
    assert_allclose(covariance(gram, scales, 0), np.diag(scales**2))
    assert np.linalg.eigvalsh(covariance(gram, scales, THETA_MAX))[0] > 0


def test_spectral_likelihood_matches_full_cholesky_density() -> None:
    rng = np.random.default_rng(102)
    gram = unit_gram(rng.normal(size=(7, 4)))
    residuals = rng.normal(size=(32, 7)) * np.arange(1, 8) * 0.01 + 0.003
    stats = block(residuals, gram)
    assert_allclose(stats.scales, np.sqrt(np.mean(residuals**2, axis=0)))
    for theta in (0, 0.2, 0.8, 0.999):
        expected = multivariate_normal.logpdf(
            residuals, cov=covariance(gram, stats.scales, theta)
        ).sum()
        assert_allclose(stats.score(theta), expected, rtol=1e-10)
    factor = rng.normal(size=(7, 2))
    factor = factor @ factor.T * 1e-5
    assert_allclose(
        forecast_covariance(residuals, gram, 0, factor),
        factor + np.diag(np.mean(residuals**2, axis=0)),
    )


def test_pooled_calibration_recovers_theta_across_different_geometries() -> None:
    rng = np.random.default_rng(48)
    blocks = []
    for firms in (7, 11):
        gram = unit_gram(rng.normal(size=(firms, 4)))
        scales = rng.uniform(0.01, 0.05, firms)
        residuals = rng.multivariate_normal(
            np.zeros(firms), covariance(gram, scales, 0.45), size=10000
        )
        blocks.append(block(residuals, gram))
    theta, score = fit(blocks)
    assert abs(theta - 0.45) < 0.025
    assert score >= sum(item.score(0) for item in blocks)


def test_calibration_retains_exact_endpoints_and_zero_when_unidentified() -> None:
    gram = np.array([[1, 0.5], [0.5, 1]], dtype=float)
    orthogonal = np.array([[1, 1], [1, -1], [-1, 1], [-1, -1]], dtype=float)
    assert fit([block(orthogonal, gram)])[0] == 0
    collinear = np.array([[1, 1], [-1, -1], [1, 1], [-1, -1]], dtype=float)
    assert fit([block(collinear, gram)])[0] == THETA_MAX
    assert fit([block(collinear, np.eye(2))])[0] == 0
    with pytest.raises(ValueError, match="at least one"):
        fit([])


def test_rms_and_dependence_domains_fail_explicitly() -> None:
    with pytest.raises(ValueError, match="strictly positive"):
        rms_scales(np.zeros((5, 2)))
    with pytest.raises(ValueError, match="at least two"):
        rms_scales(np.ones((1, 2)))
    with pytest.raises(ValueError, match="theta"):
        covariance(np.eye(2), np.ones(2), 1)


def test_full_pcoa_reconstructs_chords_and_component_portfolio_identity() -> None:
    rng = np.random.default_rng(76)
    gram = unit_gram(rng.normal(size=(9, 4)))
    result = pcoa(gram, tickers=tuple("ABCDEFGHI"), components=9)
    coordinates, weights = result.coordinates, result.weights
    assert result.rank == result.components == 4
    assert result.variance_share == pytest.approx(1)
    assert_allclose(coordinates @ coordinates.T, result.gram, atol=1e-14)
    assert_allclose(
        np.sum((coordinates[:, None] - coordinates[None]) ** 2, axis=-1),
        2 * (1 - gram),
        atol=1e-14,
    )
    assert_allclose(weights.T @ coordinates, np.eye(4), atol=1e-14)
    assert_allclose(weights.sum(axis=0), 0, atol=1e-14)
    assert_allclose(weights, coordinates @ np.linalg.inv(coordinates.T @ coordinates))


def test_pcoa_component_cap_deficient_rank_and_zero_rank() -> None:
    rng = np.random.default_rng(20)
    full = pcoa(unit_gram(rng.normal(size=(12, 8))))
    assert full.rank == 8
    assert full.components == 5
    assert 0 < full.variance_share < 1
    deficient = pcoa(unit_gram(rng.normal(size=(8, 2))))
    assert deficient.rank == deficient.components == 2
    empty = pcoa(np.ones((6, 6)))
    assert empty.rank == empty.components == 0
    assert empty.coordinates.shape == empty.weights.shape == (6, 0)
    assert empty.variance_share == 0


def test_pcoa_orientation_uses_lexical_ticker_ties() -> None:
    gram = np.array([[1, -1], [-1, 1]], dtype=float)
    result = pcoa(gram, tickers=("Z", "A"))
    assert result.coordinates[1, 0] > 0
    reordered = pcoa(gram, tickers=("A", "Z"))
    assert reordered.coordinates[0, 0] > 0
    assert_allclose(result.coordinates, -reordered.coordinates)


def test_pcoa_spectrum_and_projection_are_equivariant_to_firm_permutation() -> None:
    rng = np.random.default_rng(7)
    gram = unit_gram(rng.normal(size=(9, 4)))
    tickers = tuple("ABCDEFGHI")
    first = pcoa(gram, tickers=tickers)
    order = rng.permutation(9)
    second = pcoa(gram[np.ix_(order, order)], tickers=tuple(tickers[index] for index in order))
    assert_allclose(first.eigenvalues, second.eigenvalues, atol=1e-14)
    assert_allclose(first.coordinates[order], second.coordinates, atol=1e-14)
