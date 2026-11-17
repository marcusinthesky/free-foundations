---
name: python-testing
description: Use when writing, changing, reviewing or organizing Python tests, pytest fixtures or Hypothesis strategies in Free Foundations.
---

# Python testing

## Workflow

1. Inspect the code contract, nearby tests, `conftest.py`, shared fixtures and
   strategies, the package's test README, and pytest configuration. Reuse an
   existing test or generator when it covers the behavior; extend it only for a
   distinct, meaningful risk. Do not add tests for trivial or reversible changes
   just to increase counts, or tests that restate implementation details.
2. Prefer Hypothesis for input variation when a general property is meaningful.
   Prefer a small explicit example for a single known boundary, regression or
   command smoke check. Decide the expected outcome independently of the code
   under test. Use tiny representative data, bounded generators and the smallest
   appropriate test boundary. Assert public behavior, including error contracts.
3. Place a test beside its source owner under the mirrored `tests/` layout:
   `src/free_foundations/study/sec.py` owns `tests/study/test_sec.py` and feature
   files such as `tests/study/test_sec__parsing.py`; a subpackage's `__init__.py`
   owns `tests/test_<subpackage>.py`. `just python::layout` enforces this. Reuse
   existing factories and strategies first. Keep a helper local until several
   tests need it; put cross-module strategies in `tests/_strategies.py` and
   shared pytest fixtures in the nearest common `conftest.py`. Place a fixture
   at broader scope only when its state is safe to share. Measure costly setup
   before broadening scope; avoid creating generic fixture frameworks.
4. Arrange inputs and prerequisites, act on the behavior, and assert observable
   results (AAA). Cleanup belongs in a fixture finalizer or context manager.
   Label each phase with an `# Arrange`, `# Act` or `# Assert` comment, as in
   the example below. Favor DAMP: clear names and visible expected values can
   justify a little repetition.
5. Give each new or modified test exactly one scope marker from the table below;
   add `slow` or `external` only when applicable. Mark a class or module only
   when every inherited test has the same scope. Never stack or override scope
   markers, including inherited marks. Before using markers, register the six
   names in the owning pytest configuration; unknown names fail under
   `--strict-markers`. This skill defines the policy; it does not mean the
   current unmarked suite already enforces it. Migrate existing tests deliberately
   if adding a collection-time enforcement hook.
6. During development, run the smallest relevant test or selection and check
   its output. Before handoff run the repository's required full checks, including
   the complete non-Testmon suite. Run any affected slow or external tests when
   their prerequisites and authorization are available; report what was not run
   and why. A targeted pass is not evidence that the full suite passed.

## Markers

Use only these six custom markers. Built-in pytest mechanisms such as
`parametrize`, `skipif` and `xfail` remain available for their intended purposes.
Scope describes the boundary the assertions exercise, not the number of files,
the use of Hypothesis, or the choice of a reference oracle.

| Marker | Rule |
| --- | --- |
| `unit` | Exactly one scope: an isolated operation or small self-contained behavior. |
| `component` | Exactly one scope: one coherent subsystem or component through its public behavior. |
| `integration` | Exactly one scope: interactions across components or a real dependency boundary. |
| `e2e` | Exactly one scope: a complete user-visible workflow through the public CLI or API. A CLI help check alone is not end-to-end. |
| `slow` | Optional execution label: the complete test, including setup, teardown and generated examples, consistently exceeds two seconds on the normal local environment. Confirm with repeated pytest duration reports; a single noisy measurement is not enough. |
| `external` | Optional execution label: the test accesses a live network service or external account. Use even if it is usually fast; require explicit opt-in and appropriate credentials. A local temporary file, subprocess or fake alone does not qualify. |

`slow` and `external` are independent and may accompany any one scope. Do not
invent custom markers for regression, reference, property, smoke, tools or
implementation techniques; communicate those in descriptive test names and
assertions. Run fast local iteration with `-m "not slow and not external"`
after the markers are registered. Full checks must not silently omit slow tests;
external tests need a separate explicit lane and must not mutate live services
without authorization.

## Hypothesis examples and fixtures

Hypothesis strategies generate values; pytest fixtures manage resources. If
Hypothesis is absent, add it to the locked workspace development dependencies
when introducing the first test that uses it. Search
for reusable strategies or an appropriate first-party Hypothesis extra before
adding one. Compose built-in strategies, use `@composite` for dependent values,
and generate valid inputs directly rather than filtering most examples. Keep
sizes bounded and counterexamples understandable. Preserve an important known
failure using `@example` or an explicit regression; do not duplicate a property
with a long list of examples that establish the same behavior.

A function-scoped pytest fixture runs once per test function, not once per
`@given` example. For per-example mutable resources, create and clean them inside
the test, for example with `TemporaryDirectory()`. Reuse immutable shared data
only when safe. Do not suppress health checks or disable deadlines globally to
make a test pass; investigate the cause and document a narrowly justified
exception. Choose explicit settings or a shared profile only when warranted by
measured cost. Preserve failing examples and replay information as appropriate.

This self-contained example illustrates a small property, AAA and the scope
marker; it uses the standard-library URL parser rather than a study module:

```python
from string import ascii_lowercase, digits
from urllib.parse import urlsplit

import pytest
from hypothesis import example, given, strategies as st


@pytest.mark.unit
@example(host="news")
@given(host=st.text(alphabet=ascii_lowercase + digits, min_size=1, max_size=20))
def test_url_hostname_normalizes_ascii_case(host: str) -> None:
    # Arrange: build a URL with an uppercase hostname.
    url = f"https://{host.upper()}.example/article"

    # Act: extract the hostname.
    hostname = urlsplit(url).hostname

    # Assert: the hostname is lowercase.
    assert hostname == f"{host}.example"
```

Use a real local Parquet or filesystem boundary for a small integration test
when that interaction matters; use a stub or fake for costly or nondeterministic
remote services. A fake cannot establish that the real service works. Keep
randomized tests independent of execution order; for numerical or sampling
claims define tolerances and uncertainty rather than requiring arbitrary
bit-for-bit agreement across environments.

Consult the Hypothesis [tutorial](https://hypothesis.readthedocs.io/en/latest/tutorial/),
[how-to guides](https://hypothesis.readthedocs.io/en/latest/how-to/),
[strategies and API reference](https://hypothesis.readthedocs.io/en/latest/reference/)
and [extras](https://hypothesis.readthedocs.io/en/latest/extras.html) when
choosing or debugging a strategy.
