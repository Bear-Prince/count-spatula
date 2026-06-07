## Why

The project currently has exploratory scripts and notebooks, but lacks a stable,
user-facing workflow to generate kitchen utensil bins as printable STL
artifacts. This change is needed now to provide a repeatable, parameter-driven
interface aligned with Gridfinity standards that can be tested, versioned, and used in releases.

## What Changes

- Introduce a parametric model definition for kitchen utensil bins that follows Gridfinity-compatible dimensions and interfaces.
- Add a simple command-line interface to configure bin dimensions and export one
or more STL files.
- Define supported parameter ranges, defaults, and validation behavior for safe,
printable output.
- Establish predictable output naming and file placement for generated STL
artifacts.
- Add acceptance-focused tests that verify parameter handling, geometry
generation behavior, and export outcomes.

## Capabilities

### New Capabilities

- `gridfinity-parametric-utensil-bin`: Generate Gridfinity-compatible kitchen
utensil bin geometry from validated parameters.
- `stl-export-cli`: Provide a simple CLI that accepts parameters and produces
STL files with deterministic output behavior.

### Modified Capabilities

- None

## Impact

- Affected code: `chop_bin.py`, `main.py`, and new/updated CLI support modules
if needed.
- Affected tests: new or expanded tests in `tests/` for parameter validation,
CLI behavior, and export flow.
- Dependencies: continues using `gridfinity-build123d`; no new external runtime
dependency expected for initial scope.
- User-facing behavior: shifts from script/notebook-first usage to a documented
CLI for parametric STL generation.
