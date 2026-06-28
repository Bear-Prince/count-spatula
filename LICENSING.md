# Project context: licensing & attribution

This project is a **build123d-based generator for Gridfinity-compatible kitchen/cutlery
bins**, built on top of `gridfinity_build123d`. Some generated bins are derived from a
third party's design; others (e.g. the IKEA chopping-board bin) are original. Because
those two categories carry **different licenses**, this file records the rules so they
aren't accidentally mixed. Read this before adding licenses, headers, presets, or upload
tooling.

## The core split: code vs. models

Code and generated models are separate works and take different license types.

- **Generator code → Apache License 2.0.** This is software; CC is not used for code.
- **Generated model files (STL/STEP) → depends on provenance** (see next section).

## Model licensing rules

Provenance decides the license. Do not blanket-apply one license to all bins.

- **Bins derived from "The Next Layer" Gridfinity Complete Kitchen Collection**
  (i.e. that reproduce its cut-out profiles / distinctive design): **CC BY-SA 4.0,
  mandatory.** The source is CC BY-SA 4.0, whose ShareAlike term requires adaptations
  to use the same license. These cannot be made more restrictive *or* more permissive,
  and no extra restrictions/tech measures may be added.
- **Original bins** (e.g. the IKEA chopping-board bin, and any bin whose geometry comes
  from our own measurements and our own profiles): **our choice.** Not required to be
  BY-SA. May be BY-SA anyway for simplicity, but that is a choice, not an obligation —
  flag it as such, don't silently force it.

## Keeping the Apache code clean

The generator code stays Apache 2.0 **only if it doesn't become the vehicle for the
third party's creative design.**

- Generic parametric logic (produces shapes from dimensions): **Apache 2.0.**
- Any preset/data files that hardcode The Next Layer's specific cut-out parameters or
  reproduce their design: treat as **CC BY-SA 4.0 assets**, even inside this repo.
  Keep them in a clearly separated, clearly marked location with attribution.

Recommended layout:

```text
/src        Apache 2.0 generator code
/presets    BY-SA assets that reproduce The Next Layer designs (marked + attributed)
/LICENSE    Apache 2.0 (the code license)
/LICENSES/CC-BY-SA-4.0.txt   full text for the BY-SA assets/models
/CREDITS.md  attribution + lineage (see below)
```

## "Independent work" test (when a bin can be our own license)

A bin only *has* to be BY-SA if it's a derivative of The Next Layer's protected
expression. Raw functional dimensions (a slot sized to fit a real teaspoon) are facts
and aren't copyrightable; the protected part is creative expression (their distinctive
finger-slide profiles, stylized thick walls, modular end-cap look).

So a bin is genuinely independent — and free to carry our own license — when its
dimensions come from our own measurements AND its profiles/styling/stacking design are
our own, leaving only the *idea* of Gridfinity kitchen bins + functional facts in common.

Important: do NOT nudge dimensions cosmetically to "look less derivative." That doesn't
change derivative status and is against the spirit of the project. Independence must be
real (own measurements, own expression), not disguised.

## Attribution requirements (CC BY-SA 4.0)

For any derived model and in the repo README, include:

- Credit to **The Next Layer (JonathanLevi)**.
- A **link to the source model** on Printables.
- A **link to the CC BY-SA 4.0 license**: <https://creativecommons.org/licenses/by-sa/4.0/>
- A statement that **changes were made** (BY-SA requires indicating modifications).
- Preservation of any existing notices.
- A mark that our version is also **CC BY-SA 4.0**.

Also credit **atmmilani** ("Gridfinity Blanks", Thingiverse thing:5758082, CC BY 4.0)
with a link to the source and to <https://creativecommons.org/licenses/by/4.0/> . CC BY's
attribution requirement persists through downstream adaptations, so this credit is
required (not just courteous), even though The Next Layer is our direct source.

## Lineage (credit the chain)

Even where not legally required, credit the chain — it's how remix culture stays healthy:

```text
Zack Freedman (Gridfinity, MIT)
  └─ atmmilani — "Gridfinity Blanks" (Thingiverse, CC BY 4.0)   [The Next Layer's source]
       └─ The Next Layer — "Gridfinity Complete Kitchen Collection" (CC BY-SA 4.0)
            └─ THIS PROJECT (stackable + original additions; derived bins are BY-SA)
```

## Dependency & source licenses (verified)

- Gridfinity (Zack Freedman) — **MIT**
- `gridfinity_build123d` (Ruudjhuu) — **MIT**
- `build123d` (gumyr) — **Apache 2.0**
- The Next Layer "Gridfinity Complete Kitchen Collection" — **CC BY-SA 4.0**
- atmmilani "Gridfinity Blanks" (Thingiverse, thing:5758082) — **CC BY 4.0** (upstream
  source The Next Layer remixed)

Chain is confirmed license-compatible: atmmilani (CC BY) → The Next Layer (CC BY-SA) →
this project (CC BY-SA). CC BY material can validly be incorporated into a BY-SA
adaptation, so there is no upstream conflict. Notably there is **no NonCommercial term
anywhere in the chain**, so no commercial restriction propagates down.

For MIT deps: retain their copyright + permission notice if their source is redistributed.
For build123d (Apache 2.0): if its code is redistributed, retain notices, include the
license, state changes, and preserve any NOTICE file.

## Distribution / upload constraint

Derived (BY-SA) models may only be posted to platforms that **preserve CC BY-SA 4.0**.
Printables and Thingiverse are fine. **Do not** publish BY-SA models under any exclusive
or restrictive platform license (e.g. MakerWorld's exclusive Standard Digital File
License) — "ShareAlike" and "exclusive" are incompatible. Any future upload/automation
tooling must filter out platforms that won't keep the BY-SA license, and should respect
each site's Terms of Service regarding automated/bulk uploads.

---

*Note: this reflects a working understanding, not legal advice. The "functional vs.
creative" and "derivative vs. independent" lines are genuinely fuzzy for parametric 3D
designs; get a professional opinion if the project grows beyond hobby scope.*
