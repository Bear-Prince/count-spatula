## Context

The `knife-blade-block` capability shipped in v0.2.0. Its spec, the README, and the `deck_height_mm`
docstring all state that a user-supplied blank matching the block's height keeps knives level. Physical
UAT of the first print disproved it. The geometry is fine; the description of it is not.

## Goals / Non-Goals

**Goals:**

- The spec, README, and docstring describe how the block actually supports a knife.
- The correction is recorded as a change, so the archive shows "we shipped this, then knew better".

**Non-Goals:**

- Any geometry, parameter, or CLI change. Nothing about the printed part is wrong.
- Renaming `deck_height_mm`.

## Decisions

### Decision 1: Correct the description, not the code

`deck_height_mm` returns `taper_depth + relief_depth + min_deck_thickness`, which is genuinely the
height of the block's top face, and its test asserts exactly that. Both stay. *Rationale:* the value was
never wrong; the claim about what it is *for* was. Changing correct code to match a corrected
description would be the wrong way round.

### Decision 2: Keep the name `deck_height_mm`

*Rationale:* "deck height" accurately names the top face. A rename would churn the property, its test,
the README example and the docstring for no gain in accuracy, and would make the diff look like a
behaviour change when nothing behaves differently. *Alternative considered:* `top_face_height_mm` -
marginally more literal, not worth the churn.

### Decision 3: Two requirements change, not one

The false interface lives in "Generate only the block", but "holds knives by the blade" separately
claims the knives "rest along their length", which is the same misconception in different words.
*Rationale:* correcting one and leaving the other would leave the wrong mental model in the spec, which
is exactly how this survived review the first time. *Maps to:* both MODIFIED requirements in the delta.

### Decision 4: Name the taper as the cause, not handle weight

UAT showed the two knives that tip are the curved carving knives, and the mechanism is that a blade
tapering to a point drops away from the slot as it narrows, so a shorter run of it is gripped. Handle
weight matters only as the lever acting against that reduced grip. *Rationale:* "heavy handles rock" is
not actionable - a reader cannot tell which of their knives is affected. "Blades that taper to a point"
is something they can look at and check.

## Risks / Trade-offs

- **A reader who already built to the old guidance has a useless 18 mm blank.** → Acceptable: the
  capability shipped days ago, the Thingiverse listing was corrected before publication, and the
  corrected text explains why nothing goes there.
- **The archived v0.2.0 change still contains the wrong claim.** → Correct and intended. Archives are
  one-way in this repo; the history should honestly show the original and this correction.
