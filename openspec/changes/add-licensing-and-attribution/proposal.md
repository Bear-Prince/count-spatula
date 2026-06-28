## Why

The project ships two distinct kinds of work — generator code and generated 3D
models — and the models split further by provenance: some bins reproduce The
Next Layer's "Gridfinity Complete Kitchen Collection" (a CC BY-SA 4.0 design),
while others (e.g. the IKEA chopping-board bin) are our own. Today the repository
carries no `LICENSE`, no attribution, and no rule keeping these categories apart.
Without that, contributors can silently mix a copyleft third-party design into
permissively-licensed code, publish ShareAlike models to platforms that strip the
license, or redistribute dependencies without their required notices. Licensing
must be established before the project is shared or any upload tooling is built.

## What Changes

- Add `LICENSE` (Apache 2.0) covering the generator **code**.
- Add `LICENSES/CC-BY-SA-4.0.txt` (full license text) covering the generated
  **model files**. All generated models are CC BY-SA 4.0: derived bins by
  obligation (ShareAlike), original bins by our explicit choice for repo-wide
  uniformity.
- Add `CREDITS.md` recording the attribution chain (Zack Freedman → atmmilani →
  The Next Layer → this project) and the BY-SA attribution block for derived bins.
- Add a `NOTICE` file and retain the MIT/Apache notices of redistributed
  dependencies (`gridfinity_build123d`, `build123d`).
- Establish the **code-vs-models** rule and the **provenance** rule as documented
  policy: generic parametric logic stays Apache 2.0; any preset/data that hardcodes
  The Next Layer's distinctive cut-out parameters is treated as a CC BY-SA 4.0
  asset, kept in a clearly-marked, separately-licensed location.
- Tag each preset/model with its provenance ("derived" vs "original") and the
  license that follows from it, so the right notices can be emitted automatically.
- Update `README.md` with a licensing summary, the dependency-license table, and
  the derived-model attribution requirements.
- Record the distribution constraint: BY-SA models may only be posted to
  platforms that preserve CC BY-SA 4.0 (no MakerWorld-style exclusive licenses);
  any future upload tooling must enforce this.

## Capabilities

### New Capabilities

- `licensing-and-attribution`: The project's licensing scheme and the rules that
  keep code (Apache 2.0) and models (CC BY-SA 4.0) correctly licensed by
  provenance — which license applies where, what attribution each derived model
  must carry, how dependency notices are retained, and which distribution targets
  are permitted for ShareAlike models.

### Modified Capabilities

<!-- None. No existing spec's requirements change; licensing is additive. -->

## Impact

- **New files**: `LICENSE`, `NOTICE`, `LICENSES/CC-BY-SA-4.0.txt`, `CREDITS.md`.
- **Docs**: `README.md` gains a licensing/attribution section.
- **Presets/models**: presets gain provenance + license metadata; derived presets
  may need relocating into a clearly-marked, separately-licensed area.
- **Packaging**: `pyproject.toml` `license`/classifier metadata set to Apache 2.0.
- **Dependencies**: no new runtime deps; existing MIT/Apache deps gain retained
  notices. Provenance facts are already verified in project context.
- **Future tooling**: any upload/automation feature inherits the platform-filter
  constraint defined here.
- Not legal advice; the functional-vs-creative line for parametric models is fuzzy
  and may warrant professional review if the project outgrows hobby scope.
