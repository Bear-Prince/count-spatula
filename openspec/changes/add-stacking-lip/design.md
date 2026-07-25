## Context

`KitchenBin` builds its own walls on top of `gridfinity_build123d.BaseEqual`; it does not use that library's
`Bin` class. That matters here, because `Bin` accepts a `lip=StackingLip()` argument and does the work for
us — a route we cannot take without rewriting how our bins are constructed.

Fortunately `StackingLip` is not coupled to `Bin`. Its whole interface is:

```python
StackingLip().create(path: Wire) -> BasePartObject
```

It sweeps the Gridfinity profile along whatever closed wire it is given, and `Bin` merely happens to pass
its own top rim. We can pass ours.

Three facts were established empirically against the pinned library before writing this design:

1. **The sweep works on our geometry.** A prototype swept `StackingLip` along a `KitchenBin`-style wall's
   top outer wire and produced a valid solid with an unchanged 83.50 × 167.50 mm footprint.
2. **The lip adds ~4.117 mm, not the nominal 4.4 mm.** `StackingLip.create` applies `fillet(vertex, 0.2)`
   to the profile apex. The published reference states "+~4.4mm" with a tilde, so this is within the
   standard's own tolerance — but tests must assert the measured value, not the nominal one.
3. **Side cutouts fragment the rim.** A bin with `cutouts_enabled=True` has **two** disconnected faces at
   its top Z, not one. There is therefore no single closed wire to sweep on a cut bin — and the chop-board
   preset, the bin this change most wants to serve, always has cutouts.

Fact 3 is the crux, and is almost certainly what made this look "too complicated" the first time round.

## Goals / Non-Goals

**Goals:**

- An opt-in stacking lip available to every bin type, including cutout-bearing presets like `chop-board`.
- Conformance to the Gridfinity standard by composing the upstream `StackingLip`, not by authoring profile
  geometry ourselves.
- Complete independence from pocket shape, pocket corner radius, and divider layout.
- Zero change to any existing output when the flag is not passed.

**Non-Goals:**

- Baseplates, or the `PLATE` variant of the stacking profile. Bins only.
- A lip on any rim other than the outer top rim (no pocket-edge or divider-top lips).
- Re-plumbing `KitchenBin` onto `gridfinity_build123d.Bin`. That is a larger refactor with its own UAT
  burden, and is not required to ship this.
- Changing the default height semantics. `effective_height_mm` continues to mean wall height above the
  inner floor, with the lip sitting above it.

## Decisions

### Decision 1: Build the lip before the cutout subtraction, not after the part is finished

The originating idea was to add the lip "after the bin has been generated". That instinct is right about
*coupling* — the lip is genuinely an independent step that needs nothing from the pocket or dividers — but
it cannot be implemented literally as a post-pass on the completed part, because of fact 3 above: once the
cutouts are subtracted, the rim is two open arcs and there is no closed wire left to sweep.

The build order therefore becomes:

1. Extrude the walls (unchanged).
2. Add interior dividers via `_add_interior` (unchanged).
3. **Sweep the lip along the still-intact top outer wire.** ← new step
4. Subtract the side cutouts, now sized to cut through the lip as well.

The lip step still knows nothing about pockets or dividers — it reads only the top face's outer wire — so
the decoupling the idea was reaching for is fully preserved. Only the *ordering* is constrained.

**Alternative considered:** sweep along an analytically-reconstructed outer rounded-rectangle wire after
the cutouts, then re-subtract the cutout from the lip alone. This permits a literal post-pass, but it
duplicates the outer-profile derivation in a second place where it can silently drift from the wall sketch,
and it performs the same boolean twice. Rejected as strictly more fragile for no benefit.

### Decision 2: Extend the cutout height so the slot cuts through the lip

`SideCutoutProfile` is currently built with `cutout_height = top_z - floor_z`, which stops exactly at the
wall top. Left alone, the cutout would pass under a lip that now sits above it, leaving the lip bridging
across the open handle slot — an unsupported span over fresh air that both blocks the handle opening and
prints badly.

When a lip is present, the cutout height must extend past the top of the lip. The cutout's rim fillet
geometry is unaffected: the flare and its filleted corners are anchored to the *floor*-relative dimensions,
and the extra height is added above, where the profile is already a straight vertical wall.

The result is a lip present on the two uncut rim segments and cleanly absent across each handle slot, which
is the correct physical outcome — a bin stacked on top bears on the intact rim.

### Decision 3: Opt-in, defaulting to off

`stacking_lip: bool = False` on `BinParameters`, surfaced as `--stacking-lip` on the CLI. Every current
invocation, preset, and previously exported artifact stays identical unless the flag is passed. Presets need
no special handling: `bin-presets` already specifies that overrides apply on top of preset defaults, so
`--preset chop-board --stacking-lip` works through the existing mechanism.

**Alternative considered:** default the lip on, since it is what the Gridfinity standard expects. Rejected —
it would silently change every existing output, add ~4.12 mm to every bin's height, and retroactively alter
the chop-board artifact. Not a decision to make on the user's behalf.

### Decision 4: Validate the lip's inward reach against wall thickness

The `BIN` profile spans `height_1 + height_3_bin` = 0.7 + 1.9 = **2.6 mm** horizontally, measured inward
from the outer wall face. Our default wall is 2 mm, so on a default bin the lip overhangs the pocket mouth
by 0.6 mm, narrowing the opening slightly relative to the pocket below.

This is normal Gridfinity behaviour — standard bins have thinner walls than the lip is deep, and the
prototype confirms a 2 mm wall still yields a valid solid. It is not an error. But it is surprising enough
to warrant a documented rule rather than a silent geometry change, and on a sufficiently thin wall the lip
would consume the entire wall and reach past the pocket edge.

The chop-board preset is unaffected: its walls are 3.75 mm (X) and 15.75 mm (Y), comfortably clear of 2.6 mm.

## Risks / Trade-offs

- **A lip on a cutout bin is discontinuous** → By design, not a defect; a stacked bin bears on the intact
  rim segments. Worth stating explicitly in the spec so it is never mistaken for a geometry bug.
- **Height growth may newly trip the print-bed warning** → Correct behaviour, since `check_print_bed`
  measures the real bounding box. Called out in the proposal so it is not read as a regression.
- **The 4.117 mm figure is a property of the pinned library, not the standard** → If the
  `gridfinity_build123d` pin is ever bumped, a changed apex fillet would move this number. Assert it with a
  tolerance rather than exact equality, and treat a shift as the UAT signal the CLAUDE.md pin policy
  already calls for.
- **Thin-wall overhang narrows the pocket mouth** → Validation rule per Decision 4; the default 2 mm wall
  is explicitly still allowed.
- **Sweeping along a filleted rounded-rectangle wire is the least-tested path in the upstream sweep** →
  Mitigated by the prototype (valid solid on a 3.75 mm corner radius), and by real-geometry tests covering
  both a rounded and a sharp-cornered rim.

## Migration Plan

No migration. The feature is additive and defaults to off; no existing artifact, preset, or CLI invocation
changes behaviour. Rollback is removing the flag.

## Open Questions

- Should a lipped bin's `--height-mm` be interpreted as total height *including* the lip, rather than wall
  height with the lip on top? The current design keeps the existing meaning (lip sits above the stated
  height), matching upstream `Bin`, whose docstring notes that lip size "is not included in height". Worth
  confirming this matches expectations before implementation, since it affects how a lipped bin is sized to
  a target overall height.
