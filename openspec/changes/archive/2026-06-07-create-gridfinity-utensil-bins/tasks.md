## 1. Parameter Contract and Validation

- [x] 1.1 Define a typed parameter model for Gridfinity utensil bins with documented defaults (AC: geometry defaults).
- [x] 1.2 Implement validation rules for supported ranges and incompatible value combinations (AC: validation errors).
- [x] 1.3 Add unit tests for valid explicit parameters and defaulted parameter behavior (AC: explicit and default geometry).
- [x] 1.4 Add unit tests for out-of-range and incompatible parameter failures with actionable messages (AC: invalid inputs).

## 2. Geometry Generation Integration

- [x] 2.1 Refactor generation orchestration so validated parameters flow into `chop_bin.py` as the geometry source of truth.
- [x] 2.2 Preserve baseline default geometry behavior with regression-focused assertions.
- [x] 2.3 Add tests that assert geometry generation succeeds for representative valid parameter sets.

## 3. CLI and STL Export Flow

- [x] 3.1 Implement a simple CLI entrypoint in `main.py` (or delegated module) with explicit named options.
- [x] 3.2 Implement deterministic output path/name behavior when output is omitted (AC: default output destination).
- [x] 3.3 Implement STL export execution path from CLI command to file creation (AC: single STL export).
- [x] 3.4 Implement CLI non-zero exit handling and actionable error output for validation/export failures.
- [x] 3.5 Add CLI tests for successful export, default naming, validation failure, and filesystem write failure scenarios.

## 4. Documentation and Verification

- [x] 4.1 Update usage documentation with CLI examples for explicit parameters and default behavior.
- [x] 4.2 Run `uv run ruff check .` and resolve all lint findings.
- [x] 4.3 Run `uv run pytest` and ensure all new and existing tests pass.
- [x] 4.4 Verify generated artifact behavior manually with at least one sample command and output STL.
