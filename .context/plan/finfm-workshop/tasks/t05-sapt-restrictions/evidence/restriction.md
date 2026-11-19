---
description: A spatial-error pricing restriction and a synthetic arithmetic check.
---

# Spatial-error mean restriction

For a fixed formation and ordered roster, let excess returns satisfy `r_t = B f_t + α + u_t`, `u_t = P ε_t`, `P = (I − ρW)⁻¹`, with `E[ε_t] = 0`, finite moments and invertible `I − ρW`. The maintained approximate-factor APT premises in [theory](../../t01-theory/evidence/theory.md) additionally require diversified residual risk, admissible portfolios, no asymptotic arbitrage and traded factors or a stated spanning assumption. With `μ = E[r_t]`, a priced-factor specification imposes `μ = B π + α`, where the exact null is `α = 0` and the approximate claim requires a separately specified asymptotic bound on diversified pricing errors. Under this parameterization π = E[f_t] is the vector of factor risk prices in return units per period. B is the **untransformed** factor loading matrix: P propagates residuals, not factor exposures. An intercept or zero-beta rate would change the design and must be specified and identified separately.

Separately, with `Cov(f_t, ε_t) = 0`, `Cov(f_t) = Ω`, and `Cov(ε_t) = D`, the covariance restriction is `Cov(r_t) = B Ω Bᵀ + P D Pᵀ`; diagonal D is a further model assumption, not a pricing consequence. Invertibility and a spatial covariance fit alone do not identify π or establish the APT premises. For a fixed B with full column rank and more issuers than factors, define `π̂ = (BᵀB)⁻¹Bᵀ μ̂`, `α̂ = μ̂ − Bπ̂`, and `RMS = sqrt(α̂ᵀα̂/N)`. A joint test needs a valid covariance for the estimated restrictions, generated-loadings uncertainty, dependence and rank conditions; its critical values and approximate-null tolerance must be specified before empirical use. The historical `study/apt.py` compares zero-mean covariance scores; it is not this pricing test.

## Synthetic check

This is an exact mean-vector arithmetic fixture, not a simulated inference or a test of spatial covariance. Take N=3, one factor, B=(1,2,3), π=0.01, and a permissible SEM example W with zero diagonal and all off-diagonal entries 1/2, ρ=0.25, D=I. The restricted mean is (0.01,0.02,0.03). Inject α=(0.01,−0.02,0.01), orthogonal to B: the estimated price remains 0.01 and RMS rises from zero to sqrt(0.0002) ≈ 0.014142 per period. A component in the span of B would instead be absorbed into π and is not detectable as a pricing error by this statistic.

Reproduce from `src/python` using the locked offline workspace (the cache path is writable):

```sh
UV_CACHE_DIR=/tmp/finfm-uv-cache uv run --locked --offline --no-sync python - <<'PY'
from math import sqrt
b = (1.0, 2.0, 3.0)
mu = tuple(x * 0.01 for x in b)
error = (0.01, -0.02, 0.01)
def fit(y):
    price = sum(x * z for x, z in zip(b, y)) / sum(x * x for x in b)
    rms = sqrt(sum((z - x * price) ** 2 for x, z in zip(b, y)) / len(b))
    return price, rms
price, rms = fit(mu)
price_bad, rms_bad = fit(tuple(x + e for x, e in zip(mu, error)))
assert abs(price - 0.01) < 1e-12 and rms < 1e-12
assert abs(price_bad - 0.01) < 1e-12 and abs(rms_bad - sqrt(0.0002)) < 1e-12
print(f'restricted price={price:.6f} RMS={rms:.6f}; injected price={price_bad:.6f} RMS={rms_bad:.6f}')
PY
```

The command exited 0 and printed `restricted price=0.010000 RMS=0.000000; injected price=0.010000 RMS=0.014142`. It establishes only arithmetic recovery and sensitivity for this known-loading fixture; no empirical pricing claim follows.
