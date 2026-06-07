# Design

## Context

The repository currently supports geometry exploration via scripts and
notebooks, but does not provide a stable contract for
parametric Gridfinity-compatible utensil bin generation or for repeatable
CLI-based STL export. The change introduces a
product-facing workflow where users can request a bin by parameters and receive
deterministic STL artifacts suitable for 3D printing.

Constraints include preserving existing geometry behavior where defaults are
used, keeping the implementation Python-native, and maintaining compatibility
with the current toolchain (`build123d`, `gridfinity-build123d`, `pytest`,
`ruff`).

## Goals / Non-Goals

### Goals

- Provide a parameterized bin-generation capability aligned with Gridfinity
conventions and printable defaults.
- Provide a simple CLI that validates parameters and exports STL outputs
deterministically.
- Make requirements directly testable through scenario-oriented acceptance
coverage.
- Preserve existing default geometry behavior where equivalent defaults are
selected.

### Non-Goals

- Building a GUI or notebook-first public interface.
- Supporting non-STL export formats in this change.
- Introducing remote storage, cloud publishing, or packaging/release automation.

## Decisions

1. Introduce a dedicated parameter model for bin generation and validation
    - Rationale: Centralized validation reduces geometry/runtime errors and
      makes CLI behavior predictable.
    - Alternatives considered:
        - Validate ad hoc in CLI handlers: rejected because rules would be
        duplicated and harder to test.
        - Accept free-form kwargs directly in geometry layer: rejected because
        failures would be late and unclear.
    - Acceptance criteria mapping: supports spec outcomes for valid/invalid
      parameter handling and deterministic generation.

2. Keep `chop_bin.py` as geometry source of truth and route CLI requests through
a thin orchestration layer
    - Rationale: Preserves existing architecture intent while adding a stable
      interface.
    - Alternatives considered:
        - Move all geometry into `main.py`: rejected due to coupling and reduced
        testability.
        - Build geometry in CLI module directly: rejected because it hides core
        behavior outside primary geometry module.
    - Acceptance criteria mapping: supports requirement that CLI generation
    reflects validated geometry behavior.

3. Use explicit CLI options for grid units, wall/base values, and output path
with deterministic naming defaults
    - Rationale: Explicit options improve discoverability and allow reproducible
    commands.
    - Alternatives considered:
        - Positional-only CLI: rejected because parameters are easy to
        mis-order.
        - Config-file-only interface: rejected because it increases friction for
        simple one-off runs.
    - Acceptance criteria mapping: supports scenario coverage for user input,
    output naming, and file placement.

4. Treat STL export as a separate capability contract from geometry generation
    - Rationale: Separating concerns clarifies test boundaries and future
    extensibility for presets/batch generation.
    - Alternatives considered:
        - Single monolithic requirement: rejected because failures become hard
        to diagnose.
    - Acceptance criteria mapping: supports independent tests for geometry
    contract and export contract.

## Risks / Trade-offs

- [Risk] Gridfinity dimensional assumptions may differ from community variants.
  - Mitigation: Define defaults explicitly in requirements and provide
  documented parameters for controlled variation.
- [Risk] Backward compatibility for legacy script usage may regress.
  - Mitigation: Preserve equivalent default behavior and add regression tests
  for baseline dimensions.
- [Risk] CLI UX may become too complex if too many options are exposed at once.
  - Mitigation: Start with a minimal option set and clear defaults; defer
  advanced flags to follow-up changes.
- [Risk] STL export behavior can vary by environment/tool versions.
  - Mitigation: Standardize output naming and include deterministic acceptance
  checks around generated paths/files.

## Migration Plan

1. Introduce parameter model and validation with tests first.
2. Refactor generation flow so CLI calls validated geometry orchestration.
3. Add CLI options and deterministic output behavior.
4. Add/adjust tests for invalid inputs, geometry defaults, and STL export
outputs.
5. Update documentation to prefer CLI workflow over ad hoc script invocation.

### Rollback strategy

- Revert CLI entrypoint changes while preserving internal geometry helpers if
needed.
- Retain tests that validate existing default geometry behavior to detect
regressions during rollback.

## Open Questions

- Which subset of Gridfinity parameters should be public in v1 (minimal
practical set vs. advanced tuning)?
- Should batch generation from preset profiles be included now or tracked as a
separate follow-up change?
- Do we want output naming to include a stable parameter hash for traceability
in later releases?
