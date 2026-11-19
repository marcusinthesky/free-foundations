# January 2016 PCoA pilot: descriptive receipt

This bounded pilot uses the frozen `fernandez:tabpfn_full` state for information at the January 2016 formation, stored under quarter end **2016-03-31**. It uses the complete, sorted 967-issuer analytical roster for the geometry and for every ratio comparison. The 2015 formation's saved 878 available replication estimates are a verified subset of that roster, but are not used to select coordinates or observations. Each ratio comparison uses the finite values within those same 967 rows. The state has shape 967 × 1,024. This is one date, not evidence of temporal stability.

The pilot calls `study.experiments.inputs.load`, which verifies the prepared inventory and master contract, then `RepresentationStore`, which checks the manifest, input and implementation provenance, the state file hash, inventory, embedding validity and issuer order. Identities at baseline `793ae468309e02b5f46fc73a2ab00080464e973d`:

- Panel manifest SHA-256: `a56bd4ea963bcfd6556b75da3f769fffd875c1ce7593e776e21b1b642be594ff`.
- Representation manifest SHA-256: `eb059e01597fd5ef9db09a52c93912a100dcb76efce634eeb42dbaa75c8eefa7`.
- `data/processed/crsp-sec/representations/2016-03-31/fernandez/states.npz`: SHA-256 `7c5162f1087d57e036a711d877db95f84a063d1e2a50a55258095869f673cca5`.
- SHA-256 of sorted issuer IDs joined by newline, without a terminal newline: `f6da8285e0848edefa717028a048576c88edd7b750b29b8ddd1fe33fcba28f3e`.

Run from the repository root with the pinned environment and existing local data, without network or new encoding:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  devenv shell -- uv run --offline --project src/python --locked python \
  .context/plan/finfm-workshop/tasks/t04-pcoa-interpretation/evidence/pilot.py \
  > /tmp/ff-pcoa-pilot.json
```

The recheck after the study layout move reproduced the reported identities and
geometry in 18.78 seconds, with peak RSS of 773,680 KiB and one BLAS thread.

The script emits the complete numeric receipt to the private output path. It normalizes every state row to unit length, uses Euclidean chord distances, double-centres squared distances, and eigendecomposes the centred Gram matrix. Positive eigenvalues above `eps × n × max(abs(eigenvalue)) = 3.72e-11` define retained coordinates. There are 963 such eigenvalues and no negative eigenvalues beyond that tolerance. The smallest is −5.26e-14; summed absolute raw negative inertia is 5.26e-14, versus zero above tolerance. The maximum absolute Gram row sum is 1.83e-13. Using all retained positive coordinates, pairwise distance reconstruction has RMSE 4.88e-11 and maximum absolute error 1.83e-8. The first three eigenvalues are 173.144, 44.091 and 28.230; they account for 63.63% of positive inertia. These reconstruction checks concern the full positive eigenspace, not a three-coordinate approximation.

For each characteristic, select the latest finite value from its ten annual as-of slots, without filling missing values. The table gives Spearman correlation with PC1 and an in-sample, rotation-invariant OLS R² from regressing the characteristic's ranks on an intercept and the first three **raw** coordinates. This is a descriptive association on a potentially different observed subset for each ratio, not a null test or interval.

| Characteristic | Observed issuers | PC1 Spearman ρ | Top-three rank-response R² |
| --- | ---: | ---: | ---: |
| Market cap / assets | 960 | −0.810 | 0.926 |
| Market-to-book | 903 | −0.659 | 0.602 |
| Dividend yield | 647 | 0.155 | 0.024 |
| Debt maturity | 777 | 0.070 | 0.008 |

Eigenvector signs are arbitrary: reversing PC1 reverses each reported PC1 correlation without changing distances or explanatory fit. An orthogonal rotation of the first two coordinates and a sign reversal of the third changes their Gram matrix by at most 2.22e-16 and leaves each top-three R² unchanged to printed precision. This numerical invariance check does not establish stability across dates or identify individual rotated axes as eigenvectors.

The ratios and their histories are inputs to the encoder, and the model context label is next-quarter market cap / assets available before the query quarter. Alignment is therefore not independent validation or an input attribution. No structured null, confidence interval, exposure comparison, distance attribution, mimicking portfolio or pricing test was run. Pretrained weights postdate the sample and CompanyFacts values are revised rather than filing-date vintages. These results are retrospective, descriptive associations, not evidence that coordinates are priced factors.

## Draft R6 paragraph

For the January 2016 analytical roster of 967 issuers, principal coordinates of TabPFN's unit-sphere chord distances on Fernández characteristic histories place 63.6% of positive inertia in the first three dimensions. The full positive eigenspace reconstructs distances to numerical precision, with no negative inertia above numerical tolerance. The first coordinate has Spearman correlations of −0.81 with the latest available market-cap-to-assets ratio and −0.66 with market-to-book; signs are arbitrary. Regressing ranks of these ratios on the first three coordinates gives descriptive in-sample R² values of 0.93 and 0.60, respectively, on 960 and 903 observed issuers. Because these characteristics enter the representation, this alignment is not independent validation; a single date cannot establish stability, and the coordinates are not shown to be priced factors.
