## Why

A cleaver does not fit the knife block's holding model. Working through one in session produced a design
that holds the blade in a deep, near-constant-width channel and rests the handle on the deck, rather than
wedging the blade in a tapered V. That is a second *holding mode*, not a re-parameterisation of the first.

The archived `knife-blade-block` change anticipated this moment in its design doc's open questions:

> Revisit if a second named variant (e.g. the deferred angled-slot cleaver block) needs `--preset`-style
> switching between named parameter sets.

Worth noting that the anticipated shape and the actual one diverged: the deferred idea was an *angled-slot*
variant, whereas what the session actually arrived at is a deep straight channel carrying the load at the
handle. The trigger fired as predicted; the solution behind it did not.

## Why this is more than a preset or a few CLI flags

Two reasons, both found by inspection rather than assumed:

1. **The preset registry is typed to one parameter class.** `Preset.factory` is
   `Callable[[], BinParameters]` and `resolve_preset(name)` returns `BinParameters`
   (`cutlery_bin.py:639`, `cutlery_bin.py:675`). A cleaver preset is therefore not a new entry in the
   `PRESETS` dict — it requires generalising the registry over a second parameter type, the same way
   `BlankingPlateParameters` sits outside `BinParameters` today.

2. **It contradicts two published requirements** in the live `knife-blade-block` spec, so the work needs
   `MODIFIED` deltas, not purely `ADDED` ones:

   - **"Tapered self-centring slot"** requires each slot to be "a tapered V ... so a blade drops until its
     faces wedge against the taper and self-centre on the slot centreline". The cleaver channel is
     near-constant-width and does not wedge; the blade passes through and is carried at the handle.
   - **"Generate only the block; handles are unsupported"** states that "the knife is carried entirely by
     the blade in its slot" and that "the block's top height does NOT define a height at which a handle
     should be supported." The cleaver design does exactly the opposite, deliberately: the deck *is* the
     handle bearing surface.

   Shipping this as additive flags would leave both requirements actively false rather than correctly
   scoped to the wedge-grip mode.

## What this backlog stub is not

This is a "tracked problem, not yet designed" stub per [WORKFLOW.md](../../WORKFLOW.md)'s "Keeping a backlog
item" recipe. It intentionally has no design, deltas or tasks yet, and will not pass `openspec validate`
until those are written.

**The core premise is unvalidated.** The design rests on two physical assumptions that have not been
printed: that a handle resting on the deck reliably bears the cleaver's weight without tipping, and that the
blade slides freely in a channel of the worked-out width without binding or rattling. The dimensions reached
in session (roughly a 3.6 mm channel, ~36 mm relief depth, blade seated ~35 mm) are provisional working
numbers, recorded here only so the reasoning is not lost — they are not design decisions. Print first.

This sequencing is deliberate: the `square-corner-support` stub exists precisely because a complete,
fully-specced implementation was killed by a single UAT print. A proposal is cheap to abandon; a print is
cheaper still, and validating first means the deltas get written with real numbers and real confidence.

## Shape a real design will need to address

- **Scope the two contradicted requirements** to the wedge-grip holding mode via `MODIFIED` deltas, and add
  the sheath-and-rest mode alongside, rather than replacing or silently widening them.
- **Generalise the preset registry** over more than one parameter type. `BlankingPlateParameters` is the
  precedent for a second product type living outside `BinParameters`; decide whether presets become generic
  or whether a parallel registry is cleaner.
- **Decide what carries the load**, explicitly and in the spec: deck-bearing handle versus blade-bearing
  slot is the whole distinction between the two modes, and the existing spec currently asserts one of them
  as a global truth.
- **Revisit the edge-relief guarantee.** The existing "cutting edge does not bottom out" scenario is a
  property worth preserving in both modes, but the mechanism differs — in the cleaver design the edge floats
  because the handle stops the descent, not because a taper does.
- **Interaction with "Block prints without splitting."** That requirement promises the default block needs no
  split machinery. A cleaver channel is substantially deeper, so confirm the variant still fits a typical bed
  or state plainly that it does not.

## Non-goals

- Redesigning the existing seven-lane knife block. Its wedge-grip mode stays exactly as shipped; this adds a
  second mode beside it.
- A general "any knife shape" parameter surface. Two concrete named modes are the scope; an open-ended
  taxonomy of blade-holding geometry is not.
