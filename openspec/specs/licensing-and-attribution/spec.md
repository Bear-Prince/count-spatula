# licensing-and-attribution Specification

## Purpose

Keep the generator code (Apache 2.0) and generated model files (CC BY-SA 4.0) correctly
licensed by provenance, so a third party's protected design is never mixed into a more
permissive license and every derived model carries the attribution it requires.

## Requirements
### Requirement: Generator code is licensed under Apache 2.0

The generator code SHALL be licensed under the Apache License 2.0. A `LICENSE`
file containing the full Apache 2.0 text SHALL exist at the repository root, and
the project's packaging metadata SHALL declare the same license. Generic
parametric logic - code that produces shapes from supplied dimensions - SHALL
remain solely under Apache 2.0 and MUST NOT embed a third party's protected
creative expression.

#### Scenario: Apache license present at repository root

- **WHEN** the repository is inspected
- **THEN** a `LICENSE` file containing the full, unmodified Apache License 2.0
  text exists at the root
- **AND** `pyproject.toml` declares the project license as Apache-2.0

#### Scenario: Generic geometry code stays Apache-only

- **WHEN** a source module computes geometry purely from caller-supplied
  dimensions and contains no hardcoded third-party design parameters
- **THEN** it is covered by Apache 2.0 with no additional model-license obligation

### Requirement: Generated model files are licensed under CC BY-SA 4.0

All generated model files (STL/STEP/3MF) SHALL be licensed under
Creative Commons Attribution-ShareAlike 4.0 International. The full CC BY-SA 4.0
license text SHALL be stored at `LICENSES/CC-BY-SA-4.0.txt`. Derived bins carry
this license by ShareAlike obligation; original bins carry it by the project's
explicit choice. A derived (BY-SA) model's license MUST NOT be made more or less
restrictive, and no additional restrictions or technical measures may be applied.

#### Scenario: License text available for models

- **WHEN** the repository is inspected
- **THEN** `LICENSES/CC-BY-SA-4.0.txt` contains the full CC BY-SA 4.0 license text

#### Scenario: Derived model license is not altered

- **WHEN** a model derived from The Next Layer's design is licensed
- **THEN** it is licensed as CC BY-SA 4.0 with no added restrictions or technical
  measures, and is neither relicensed more permissively nor more restrictively

### Requirement: Models are classified by provenance

Each preset or generated model SHALL be tagged with its provenance as either
`derived` (reproduces The Next Layer's distinctive cut-out profiles or design) or
`original` (own measurements and own profiles), and with the license that follows.
Provenance MUST reflect real independence: a bin is `original` only when both its
dimensions come from our own measurements AND its profiles/styling are our own.
Dimensions MUST NOT be cosmetically altered to disguise derivative status.

#### Scenario: Preset carries provenance and license metadata

- **WHEN** a preset is defined
- **THEN** it records whether it is `derived` or `original`
- **AND** it records the resulting model license (CC BY-SA 4.0)

#### Scenario: Reproducing a third-party profile forces derived status

- **WHEN** a preset hardcodes The Next Layer's distinctive cut-out parameters
- **THEN** it is classified `derived`
- **AND** it is treated as a CC BY-SA 4.0 asset even within this repository

### Requirement: Derived models carry full attribution

Every derived (BY-SA) model and the project README SHALL carry attribution that
credits The Next Layer (JonathanLevi), links to the source model on Printables,
links to the CC BY-SA 4.0 license, states that changes were made, preserves any
existing notices, and marks the derived version as also CC BY-SA 4.0.

#### Scenario: Attribution block is complete

- **WHEN** a derived model is distributed or its attribution is reviewed
- **THEN** the attribution credits The Next Layer (JonathanLevi), links to the
  Printables source, links to the CC BY-SA 4.0 license, states that modifications
  were made, preserves prior notices, and marks the result as CC BY-SA 4.0

### Requirement: The attribution lineage is recorded

A `CREDITS.md` file SHALL record the full design lineage and dependency licenses,
even where credit is not strictly legally required, to keep the remix chain
intact: Zack Freedman (Gridfinity, MIT) → atmmilani ("Gridfinity Blanks") →
The Next Layer ("Gridfinity Complete Kitchen Collection", CC BY-SA 4.0) →
this project.

#### Scenario: Lineage documented

- **WHEN** `CREDITS.md` is inspected
- **THEN** it lists the lineage from Zack Freedman through atmmilani and
  The Next Layer to this project, with each link's license noted

### Requirement: Redistributed dependency notices are retained

The project SHALL retain the required notices of its redistributed dependencies.
A `NOTICE` file SHALL preserve the MIT copyright and permission notices for
`gridfinity_build123d` (MIT) and Gridfinity (MIT), and the Apache 2.0 notices for
`build123d` - including stating changes and preserving any upstream NOTICE file
when that code is redistributed.

#### Scenario: Dependency notices present

- **WHEN** the repository is inspected
- **THEN** a `NOTICE` file retains the MIT notices for `gridfinity_build123d` and
  Gridfinity and the Apache 2.0 notice for `build123d`

### Requirement: Distribution targets preserve ShareAlike

Derived (BY-SA) models SHALL only be published to platforms that preserve the
CC BY-SA 4.0 license. They MUST NOT be published under any exclusive or otherwise
restrictive platform license (e.g. MakerWorld's exclusive Standard Digital File
License). Any future upload or automation tooling SHALL filter out platforms that
will not keep the BY-SA license and SHALL respect each site's terms of service
regarding automated or bulk uploads.

#### Scenario: Incompatible platform is rejected

- **WHEN** a BY-SA model is targeted at a platform that imposes an exclusive or
  ShareAlike-incompatible license
- **THEN** publication to that platform is disallowed

#### Scenario: Compatible platform is permitted

- **WHEN** a BY-SA model is targeted at a platform that preserves CC BY-SA 4.0
  (e.g. Printables, Thingiverse)
- **THEN** publication is permitted, subject to that platform's terms of service

