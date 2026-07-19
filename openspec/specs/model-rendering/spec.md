# model-rendering Specification

## Purpose
TBD - created by archiving change add-readme-model-renders. Update Purpose after archive.
## Requirements
### Requirement: Render the example model set to images

The system SHALL provide a render script that builds each bin in the example model set (the `UAT.md` bin cases,
plus a wave-divider cutlery bin) using the existing factories, and renders each one to a PNG in `docs/assets/`
using headless OpenSCAD at a fixed camera position, so the images are reproducible.

#### Scenario: Render the set to PNGs

- **WHEN** the render script is run on a machine with OpenSCAD installed
- **THEN** it writes one PNG per example model into `docs/assets/`, at a fixed camera angle and image size

#### Scenario: Missing render tool fails with an actionable error

- **WHEN** the render script is run and OpenSCAD (or ImageMagick, for GIF stitching) cannot be found on `PATH`
- **THEN** it exits non-zero with a message naming the missing tool and how to install it, without writing
  partial output

### Requirement: Produce a looping GIF of the model set

The system SHALL stitch rendered frames into at least one looping animated GIF (via ImageMagick) that cycles
through the example models, suitable for embedding in the README.

#### Scenario: GIF cycles the example models

- **WHEN** the render script completes successfully
- **THEN** `docs/assets/` contains a looping GIF whose frames are the example-model renders

### Requirement: README embeds the committed renders

The README SHALL embed the generated images from `docs/assets/` (files committed to the repository, so GitHub
renders them without CI involvement) with a caption noting the renders are of CC BY-SA 4.0 models, per
`LICENSING.md`.

#### Scenario: README references existing committed images

- **WHEN** the README is viewed on GitHub
- **THEN** its image references point at files that exist in `docs/assets/` in the same commit, with the licence
  caption present

