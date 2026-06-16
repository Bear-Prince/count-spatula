# Design

## Context

The repository has a working parametric bin generator for chopping boards (`chop_bin.py` +
`main.py`). That code builds all geometry by hand using build123d primitives on top of
`gridfinity_build123d.BaseEqual`. The `gridfinity_build123d` library also exposes a higher-level
`Bin` class with a `CompartmentsEqual` compartment strategy — exactly suited to open-top utensil
bins. This change introduces utensil bin support alongside the existing chopping board bin,
migrates the export path to `build123d.mesher.Mesher` (enabling 3MF), and adds a print-bed
size warning without altering any existing geometry behaviour.

## Goals / Non-Goals

**Goals:**

- Introduce a `utensil_bin.py` geometry module parallel to `chop_bin.py`, using
  `gridfinity_build123d.Bin` + `CompartmentsEqual`.
- Support both Gridfinity-standard heights (`height_in_units`, multiples of 7 mm) and
  freeform heights (`height_mm`).
- Default wall thickness of 2 mm for both outer and inner walls.
- Replace `build123d.export_stl()` with `build123d.mesher.Mesher` throughout, so that `.stl`
  and `.3mf` output paths both work for all bin types.
- Add `--bed-x` / `--bed-y` CLI flags that emit a warning when the bin footprint exceeds the
  configured bed size, then continue normally.
- Maintain all existing default chopping-board bin behaviour and tests.

**Non-Goals:**

- Automatic geometric splitting of oversized bins.
- S-shaped or custom divider profiles.
- GUI, notebook-first, or batch-preset generation interfaces.
- Non-STL/3MF export formats.
- Scoop or label compartment features (deferred to a follow-up change).

## Decisions

### 1. Introduce `utensil_bin.py` as a parallel geometry module

**Rationale:** The utensil bin delegates almost all wall and base construction to
`gridfinity_build123d.Bin` + `CompartmentsEqual`. Mixing this into `chop_bin.py` would conflate
two unrelated geometry concerns and make each harder to test in isolation.

**Alternatives considered:**

- Single `bins.py` module containing both bin types: rejected because it would grow unbounded
  as more bin types are added.
- Extend `ChopBin` with an optional `mode` parameter: rejected because the chopping board and
  utensil bin share no geometry logic.

**Acceptance criterion mapping:** supports independent parameter validation and geometry
tests for each bin type.

### 2. `UtensilBinParameters` with mutually exclusive height fields

**Rationale:** The library's `Bin` class accepts either `height` (float, mm) or
`height_in_units` (int). Mirroring this at the parameter layer makes the mapping transparent
and validates the constraint before geometry construction.

```python
@dataclass(slots=True)
class UtensilBinParameters:
    grid_x: int = 2
    grid_y: int = 4
    height_in_units: int | None = 7   # 7 units × 7 mm = 49 mm
    height_mm: float | None = None    # freeform override
    div_x: int = 1
    div_y: int = 1
    wall_thickness_mm: float = 2.0
```

`validate()` raises `ValueError` if both height fields are set, or if neither is set.
A `effective_height_mm` property resolves the active value.

**Alternatives considered:**

- Single `height_mm` field with a convenience constructor: rejected because it obscures the
  Gridfinity unit concept from users working with standard heights.
- A `height_mode` enum: rejected as over-engineered for two mutually exclusive fields.

**Acceptance criterion mapping:** supports scenario coverage for both height modes and for
invalid combined height inputs.

### 3. Wall thickness via `outer_wall` and `inner_wall` in `CompartmentsEqual`

**Rationale:** `CompartmentsEqual` exposes `outer_wall` (gap from bin inner face to
compartment pocket edge) and `inner_wall` (divider thickness between compartments). Setting
both to `wall_thickness_mm` gives consistent 2 mm walls everywhere without custom geometry.

**Alternatives considered:**

- Expose `outer_wall` and `inner_wall` as separate parameters: deferred; `wall_thickness_mm`
  is sufficient for this change and avoids parameter proliferation.

**Acceptance criterion mapping:** supports scenario that generated geometry reflects the
configured wall thickness.

### 4. Replace `export_stl()` with `Mesher` throughout

**Rationale:** `build123d.mesher.Mesher` already depends on `py-lib3mf` (a transitive
dependency of `build123d`) and selects output format by file extension. A single
`export_bin(part, path)` helper that delegates to `Mesher` handles both formats with no new
dependencies and no branching on format in the caller.

```python
def export_bin(part: Shape, output_path: Path) -> Path:
    mesher = Mesher()
    mesher.add_shape(part)
    mesher.write(output_path)
    return output_path
```

This replaces the existing `export_stl(part, str(output_path))` call in `main.py`. The
chopping board bin CLI gains 3MF support for free.

**Alternatives considered:**

- Keep `export_stl()` and add a separate `export_3mf()`: rejected because it doubles the
  export surface and requires format branching in every caller.
- Use `trimesh` as a conversion layer: rejected; `py-lib3mf` is already available.

**Acceptance criterion mapping:** supports scenario coverage for `.stl` and `.3mf` output
from the same CLI invocation pattern.

### 5. Print-bed validation as a warning, not an error

**Rationale:** An oversized bin is not invalid geometry — it is a user workflow concern.
Blocking generation would prevent users from intentionally generating large bins to slice
manually in printer software. A warning to `stderr` lets the export complete while surfacing
the constraint.

**Alternatives considered:**

- Non-zero exit on bed overflow: rejected; the STL/3MF is still valid and useful.
- Automatic splitting into sub-bins: deferred; the Gridfinity base makes splitting viable in
  future, but adds scope without clear immediate benefit.

**Acceptance criterion mapping:** supports scenario that the CLI warns on overflow but
produces the output file and exits zero.

## Risks / Trade-offs

- [Risk] `Mesher` raises `Warning` (not an exception) for non-manifold meshes. Existing tests
  that mock `export_stl` must be updated to mock or use the new `export_bin` helper.
  - Mitigation: introduce `export_bin()` as the single export seam; tests mock it, not the
    Mesher internals.
- [Risk] `py-lib3mf` is a transitive dependency, not a direct one. A future `build123d`
  version change could remove it.
  - Mitigation: no action for this change; track as a packaging concern for v1.0.
- [Risk] Gridfinity dimensional assumptions (`42 mm` per unit) are hardcoded in the library
  and in `chop_bin.py`. Bed-overflow calculations must use the same constant.
  - Mitigation: derive footprint as `grid_x * 42` and `grid_y * 42`; document the assumption.

## Migration Plan

1. Add `utensil_bin.py` with `UtensilBinParameters`, `UtensilBin`, and `create_utensil_bin()`.
2. Add `export_bin()` helper in a shared export module (or in `main.py` for now); update the
   chopping board bin CLI to use it.
3. Add utensil bin subcommand to `main.py` with all CLI options and bed-size warning logic.
4. Add tests: parameter validation, CLI flow (mock `export_bin`), bed-size warning.
5. Update README with utensil bin CLI examples.

### Rollback strategy

- `utensil_bin.py` is additive; removing it has no effect on existing behaviour.
- Reverting the `Mesher` change in `main.py` restores `export_stl()` for the chopping board
  bin; the utensil bin CLI must be reverted at the same time.

## Open Questions

- Should `effective_height_mm` be exposed as a CLI `--info` output (e.g., "generating bin
  49.0 mm tall") to help users verify their height selection? Deferred to UX polish.
