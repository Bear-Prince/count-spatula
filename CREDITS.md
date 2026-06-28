# Credits and attribution

This project produces two kinds of work under two different licenses:

- **Generator code** — Apache License 2.0 (see [LICENSE](LICENSE)).
- **Generated model files** (STL/STEP/3MF) — Creative Commons
  Attribution-ShareAlike 4.0 International
  ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); full text in
  [LICENSES/CC-BY-SA-4.0.txt](LICENSES/CC-BY-SA-4.0.txt)).

All generated models are CC BY-SA 4.0: **derived** bins by obligation (the
upstream design is ShareAlike), and **original** bins by the project's deliberate
choice to keep a single model license. The original choice is not a legal
requirement and may be revisited per bin.

## Design lineage

Even where credit is not strictly legally required, we credit the whole chain —
it is how remix culture stays healthy:

```text
Zack Freedman — Gridfinity (MIT)
  └─ atmmilani — "Gridfinity Blanks" (Thingiverse, CC BY 4.0)   [The Next Layer's source]
       └─ The Next Layer (JonathanLevi) — "Gridfinity Complete Kitchen Collection" (CC BY-SA 4.0)
            └─ count-spatula — stackable + original additions; derived bins are CC BY-SA 4.0
```

The chain is license-compatible: CC BY material (atmmilani) can validly be
incorporated into a CC BY-SA adaptation (The Next Layer), which we adapt further
under CC BY-SA. There is **no NonCommercial term anywhere in the chain**, so no
commercial restriction propagates down. Note that CC BY's attribution requirement
persists through downstream adaptations, so atmmilani must be credited on derived
models even though The Next Layer is our direct source.

## Dependency and source licenses (verified)

| Work | Author | License |
| --- | --- | --- |
| Gridfinity | Zack Freedman | MIT |
| `gridfinity_build123d` | Ruudjhuu | MIT |
| `build123d` | gumyr / contributors | Apache 2.0 |
| "Gridfinity Complete Kitchen Collection" | The Next Layer (JonathanLevi) | CC BY-SA 4.0 |
| "Gridfinity Blanks" | atmmilani (Thingiverse) | CC BY 4.0 (upstream of The Next Layer) |

Dependency notices are retained in [NOTICE](NOTICE).

## Attribution for derived models

Any bin that reproduces The Next Layer's distinctive cut-out profiles or design
is **derived** and must ship with the attribution block below — both alongside
the model file and in the project README. Per CC BY-SA 4.0, the block must:
credit the author, link the source, link the license, state that changes were
made, preserve prior notices, and mark our version as also CC BY-SA 4.0. Because
The Next Layer's source (atmmilani, CC BY 4.0) carries an attribution requirement
that persists downstream, the upstream author must be credited too.

> **Derived from:** "Gridfinity Complete Kitchen Collection" by The Next Layer
> (JonathanLevi).
> **Source:** <https://www.printables.com/model/719729-gridfinity-complete-kitchen-collection-w-modular-e>
> **License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
> **Changes:** Re-modelled as a parametric Gridfinity bin and adapted
> (stackable additions; regenerated geometry). Modifications were made to the
> original design.
> **Upstream:** based in part on "Gridfinity Blanks" by atmmilani
> (<https://www.thingiverse.com/thing:5758082>),
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> **This version** is likewise licensed under CC BY-SA 4.0.

**Note:** As of this writing the repository contains **no** derived presets — the
only preset (`chop-board`) is an original IKEA chopping-board bin. The block above
is the template to ship with the first derived bin.

## Distribution constraint

Derived (CC BY-SA 4.0) models may only be published to platforms that preserve
the CC BY-SA 4.0 license — for example **Printables** and **Thingiverse**. They
**must not** be published under any exclusive or otherwise ShareAlike-incompatible
platform license (for example MakerWorld's exclusive Standard Digital File
License); "ShareAlike" and "exclusive" are incompatible. Any future upload or
automation tooling must filter out incompatible platforms and respect each site's
terms of service for automated or bulk uploads.

---

This document reflects a working understanding and is **not legal advice**. The
functional-vs-creative and derivative-vs-independent boundaries are genuinely
fuzzy for parametric 3D designs; seek a professional opinion if this project
grows beyond hobby scope.
