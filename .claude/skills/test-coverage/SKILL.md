---
name: test-coverage
description: Audits a module's source code against its existing tests to find coverage gaps, and outputs a risk-prioritized list of untested functions and missing edge cases as JSON. Use when asked to review test coverage, find untested code, identify missing tests, or audit a module's test quality. Does NOT generate test code (use a test-generator skill for that) and does NOT modify source files.
---

# Test Coverage Report

Analyzes a module's source code and its existing tests to identify coverage gaps. Outputs a prioritized list of missing tests by risk level.

This skill **reports** gaps only. It does not write test code and does not edit source files.

- Metadata: version 2.0.1 · status stable · owner qa-team · category testing · depends-on none

## When to use

Use this skill when the user wants to:

- Audit test coverage for a specific module or file
- Find untested functions or uncovered branches
- Identify missing edge cases in an existing test suite
- Get a risk-prioritized view of where tests are most needed

Do **not** use this skill to write or scaffold tests, or to change application code.

## Inputs

Gather these before running. Ask the user for any required value that is missing.

| Input | Required | Default | Meaning |
| --- | --- | --- | --- |
| `MODULE_PATH` | yes | — | Path to the source module to audit |
| `TEST_PATH` | yes | — | Path to the existing tests for that module |
| `COVERAGE_TARGET` | no | `80` | Target coverage percentage |

## Instructions

1. Read the source at `MODULE_PATH` and enumerate every exported/public function, then the internal business logic, then utilities.
2. Read the tests at `TEST_PATH` and map each test to the source behavior it exercises.
3. Identify gaps: functions with no test, branches/conditions never asserted, and missing edge cases (empty/null inputs, boundary values, error paths, async failures).
4. Apply **risk weighting** when ranking gaps: prioritize **public API functions > business logic > utils**.
5. Estimate overall coverage and compare it against `COVERAGE_TARGET`.
6. Produce the JSON report below. Do not write test code. Do not modify source files.

### Risk-scoring rubric

- `high` — public API or core business logic with no tests, or untested error paths
- `medium` — partially tested logic, missing edge cases, estimated coverage below `COVERAGE_TARGET`
- `low` — minor utility gaps, estimated coverage at or above `COVERAGE_TARGET`

## Prompt (specialist framing)

> You are a QA engineer auditing test coverage for `{{MODULE_PATH}}`.
> FOCUS: identify untested functions, missing edge cases, and risk-weighted gaps.
> DO NOT: write test code (separate skill). DO NOT: modify source files.
> RISK WEIGHTING: prioritize public API functions > business logic > utils.

## Output format

Return a single JSON object:

```json
{
  "untested_functions": [],
  "missing_edge_cases": [],
  "estimated_coverage": "N%",
  "risk_score": "low|medium|high"
}
```
