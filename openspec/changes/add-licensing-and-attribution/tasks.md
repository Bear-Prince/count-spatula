## 1. Code license (Apache 2.0)

- [x] 1.1 Add `LICENSE` at the repository root with the full, unmodified Apache License 2.0 text.
- [x] 1.2 Set Apache-2.0 in `pyproject.toml` (`license` field and/or trove classifier), replacing the placeholder project metadata.

## 2. Model license (CC BY-SA 4.0)

- [x] 2.1 Add `LICENSES/CC-BY-SA-4.0.txt` with the full CC BY-SA 4.0 license text.
- [x] 2.2 Document that all generated models (STL/STEP/3MF) are CC BY-SA 4.0 — derived by obligation, original by choice.

## 3. Dependency notices

- [x] 3.1 Add a `NOTICE` file retaining the MIT copyright/permission notices for `gridfinity_build123d` and Gridfinity (Zack Freedman).
- [x] 3.2 In `NOTICE`, retain the Apache 2.0 notice for `build123d`, state that it is used as a dependency, and preserve any upstream NOTICE content if redistributed.

## 4. Attribution and lineage

- [x] 4.1 Add `CREDITS.md` recording the lineage: Zack Freedman (Gridfinity, MIT) → atmmilani ("Gridfinity Blanks") → The Next Layer ("Gridfinity Complete Kitchen Collection", CC BY-SA 4.0) → this project.
- [x] 4.2 In `CREDITS.md`, add the derived-model attribution block: credit The Next Layer (JonathanLevi), Printables source link, CC BY-SA 4.0 license link, "changes were made" statement, preservation of prior notices, and the BY-SA mark on our version.
- [x] 4.3 Confirm the Printables source URL/author handle for each derived bin and the atmmilani "Gridfinity Blanks" terms (resolve the design's Open Questions). (Printables: model 719729; atmmilani "Gridfinity Blanks" thing:5758082 is CC BY 4.0 — its attribution requirement propagates downstream, so it is a required credit on derived models.)

## 5. Provenance metadata and asset separation

- [x] 5.1 Add a `provenance` (`derived`/`original`) and `license` field to each preset's definition.
- [x] 5.2 Classify existing presets (`chop-board` IKEA bin = `original`; any bin reproducing The Next Layer profiles = `derived`) without altering any dimensions.
- [x] 5.3 Move/mark any preset data that hardcodes The Next Layer's cut-out parameters into a clearly-marked, separately-licensed location (e.g. `presets/` with a BY-SA header), keeping the Apache code generic. (No-op: no derived presets exist yet; `chop-board` is original. The `Provenance.DERIVED` + `derived_from` fields and the CREDITS.md attribution block are in place for when one is added.)

## 6. README and distribution constraint

- [x] 6.1 Add a licensing/attribution section to `README.md`: code Apache 2.0, models CC BY-SA 4.0, the verified dependency-license table, and derived-model attribution requirements.
- [x] 6.2 Document the distribution constraint in `README.md`/`CREDITS.md`: BY-SA models only to BY-SA-preserving platforms (Printables/Thingiverse), never exclusive licenses (e.g. MakerWorld Standard Digital File License); future upload tooling must enforce this and respect site ToS.

## 7. Verification

- [x] 7.1 Run `uv run ruff check .`, `uv run pytest`, and the configured markdownlint/yamllint hooks; fix any failures introduced by the new/edited files. (ruff clean; 34 passed; markdownlint clean; no YAML changed.)
- [x] 7.2 Verify the file layout matches the spec (`LICENSE`, `LICENSES/CC-BY-SA-4.0.txt`, `NOTICE`, `CREDITS.md` present; presets carry provenance + license).
- [x] 7.3 Generate the UAT models (per `UAT.md`) and confirm each exported model can be paired with its correct license/attribution before pushing. (UAT-1..5 exported to build/; UAT-6/7 error paths return exit 2 with no file. All current models are CC BY-SA 4.0; chop-board is original.)

## 8. Review

- [ ] 8.1 Open a PR disclosing the coding agent and model used; wait for user review before merge.
