# multi-format-export Specification

## Purpose

Provide a single unified export path that writes generated bin geometry to either STL or 3MF
format for all bin types, selecting the format from the output path or format flag and handling
filesystem failures predictably.

## Requirements

### Requirement: STL and 3MF export from a single export path

The system SHALL export generated bin geometry to either STL or 3MF format, determined by the
file extension of the requested output path, using `build123d.mesher.Mesher`.

#### Scenario: Export to STL

- **WHEN** a user requests an output path ending in `.stl`
- **THEN** the system writes a valid binary STL file to that path

#### Scenario: Export to 3MF

- **WHEN** a user requests an output path ending in `.3mf`
- **THEN** the system writes a valid 3MF file to that path

#### Scenario: Export with default output path uses configured format extension

- **WHEN** a user omits the output path and specifies `--format 3mf`
- **THEN** the deterministic default filename uses the `.3mf` extension

#### Scenario: Default format is STL when no format flag is given

- **WHEN** a user omits both the output path and the `--format` flag
- **THEN** the deterministic default filename uses the `.stl` extension

### Requirement: Export applies to all bin types

The unified export path SHALL be used for both chopping board bins and utensil bins.

#### Scenario: Chopping board bin exported via Mesher

- **WHEN** a user runs the chopping board bin CLI with a `.3mf` output path
- **THEN** the system writes a valid 3MF file for the chopping board bin geometry

### Requirement: Export failure handling

The system MUST return a non-zero exit status and emit an actionable message when the export
cannot be written due to filesystem constraints.

#### Scenario: Missing output directory

- **WHEN** the output path references a directory that does not exist
- **THEN** the system exits non-zero and reports the missing directory without producing a file
