## Context

`count-spatula` produces two kinds of work that the law treats differently:
the **generator code** (software) and the **generated 3D models** (creative/
functional artifacts). The models split again by provenance — some reproduce
The Next Layer's "Gridfinity Complete Kitchen Collection" (CC BY-SA 4.0), some
are our own (e.g. the IKEA chopping-board bin). The repository currently has no
license, no attribution, and no rule keeping these apart.

The dependency and source licenses are already verified: Gridfinity
(Zack Freedman) — MIT; `gridfinity_build123d` (Ruudjhuu) — MIT; `build123d`
(gumyr) — Apache 2.0; The Next Layer collection — CC BY-SA 4.0; atmmilani
"Gridfinity Blanks" sits upstream of The Next Layer. The constraint that drives
the design is CC BY-SA 4.0's ShareAlike clause: any adaptation of a BY-SA work
must stay BY-SA, with attribution and a statement of changes, and may not gain
extra restrictions.

This is a working understanding, not legal advice; the functional-vs-creative
boundary for parametric 3D designs is genuinely fuzzy.

## Goals / Non-Goals

**Goals:**

- Apply Apache 2.0 to the generator code and CC BY-SA 4.0 to all generated models.
- Make provenance (`derived` vs `original`) an explicit, recorded property of
  every preset/model so the correct license and attribution follow automatically.
- Keep the Apache code "clean" — never let it become the carrier of a third
  party's protected design.
- Retain the required notices of redistributed MIT/Apache dependencies.
- Record the full lineage and the distribution constraint so future upload tooling
  inherits the rules.

**Non-Goals:**

- Building the upload/automation tooling itself (this change only defines the
  constraint it must obey).
- Re-measuring or re-modelling any bin to change its derivative status.
- Obtaining formal legal review (flagged as advisable beyond hobby scope, not done
  here).
- Changing any geometry behavior or CLI interface.

## Decisions

**1. Code → Apache 2.0; models → CC BY-SA 4.0; never one license for everything.**
Software and creative artifacts are separate works. CC is not used for code, and a
software license is wrong for printable models. Alternatives rejected: a single
permissive license repo-wide (impossible — BY-SA derived models cannot be
relicensed), or GPL for code (heavier than needed and not required by the MIT/
Apache dependency chain).

**2. All generated models are CC BY-SA 4.0, including original bins (user choice).**
Derived bins must be BY-SA; original bins *could* be more permissive (CC BY, CC0),
but the user chose BY-SA for everything to keep one model license to reason about.
This is recorded as a deliberate choice, not a legal obligation, so it can be
revisited per-bin later. Alternative (CC BY / CC0 for originals) was offered and
declined in favor of uniformity.

**3. Separate the BY-SA assets from the Apache code on disk.**
Generic parametric logic stays in the code tree under Apache 2.0. Any preset/data
that hardcodes The Next Layer's distinctive cut-out parameters is a BY-SA asset and
lives in a clearly-marked, separately-licensed location (e.g. a `presets/`
directory with its own license header and attribution). This prevents the Apache
code from silently absorbing the third party's creative expression. Alternative
(inline derived parameters in Apache modules) rejected — it contaminates the code
license.

**4. Provenance is data, not a comment.**
Each preset records `provenance: derived|original` plus its license and (for
derived) its attribution block. This lets the build emit the right notice
alongside each exported model and lets future upload tooling filter targets. The
`original` classification requires *real* independence (own measurements AND own
profiles); cosmetic dimension tweaks to dodge derivative status are explicitly
disallowed.

**5. Standard license-file layout.**
`LICENSE` (Apache 2.0) at root, `LICENSES/CC-BY-SA-4.0.txt` (full BY-SA text),
`NOTICE` (retained dependency notices), `CREDITS.md` (lineage + per-derived
attribution). This mirrors the SPDX/REUSE-style convention and is what scanners
and humans expect.

**6. Encode the distribution constraint now, enforce it when tooling exists.**
BY-SA models may only go to platforms that preserve BY-SA (Printables,
Thingiverse — yes; MakerWorld's exclusive license — no). This change documents the
rule in the spec; the filter is implemented when upload tooling is built.

## Risks / Trade-offs

- **Misclassifying a derived bin as original** → leaks a copyleft design into a
  weaker license. Mitigation: provenance is explicit and required per preset; the
  independence test (own measurements AND own profiles) is documented and the
  default for any bin reproducing known profiles is `derived`.
- **BY-SA-everything is stricter than needed for original bins** → some downstream
  reuse is constrained that need not be. Mitigation: recorded as a revisitable
  choice per bin, not a structural lock-in.
- **Fuzzy functional-vs-creative line** → a classification could be wrong in
  either direction. Mitigation: documented as non-legal-advice; recommend
  professional review if the project grows beyond hobby scope.
- **Stale or incomplete attribution** → BY-SA non-compliance. Mitigation: the
  attribution block is specified as a checklist (credit, source link, license link,
  changes statement, prior notices, BY-SA mark) and lives in `CREDITS.md` next to
  the lineage.
- **Dependency notices drift** as deps change → Mitigation: `NOTICE` lists each
  redistributed dependency and its license; updated when deps change.

## Migration Plan

1. Add `LICENSE`, `LICENSES/CC-BY-SA-4.0.txt`, `NOTICE`, `CREDITS.md`.
2. Set Apache-2.0 in `pyproject.toml` metadata.
3. Tag existing presets with provenance + license; relocate/mark any derived
   preset data into the separately-licensed area.
4. Update `README.md` with the licensing summary, dependency table, and derived-
   model attribution requirements.
5. No code-behavior or rollback concerns — these are additive metadata/doc files;
   reverting is a file deletion.

## Open Questions

- Confirm the exact Printables source URL and author handle for each derived bin
  to complete its attribution block.
- Confirm atmmilani "Gridfinity Blanks" terms on Thingiverse (listed as upstream;
  its specific license should be checked before relying on it).
- Final on-disk location/name for the BY-SA preset assets (`presets/` proposed).
