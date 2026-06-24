## MODIFIED Requirements

### Requirement: Print-bed size configuration

The system SHALL accept optional print-bed dimensions as CLI parameters — bed width (`--bed-x`), bed depth
(`--bed-y`), and an optional maximum print height (`--bed-z`) — so that a generated model can be checked against
the printer's build volume.

#### Scenario: Configure print bed via CLI

- **WHEN** a user provides `--bed-x 235` and `--bed-y 235` (optionally with `--bed-z 250`)
- **THEN** the system stores those dimensions and uses them to evaluate the generated model

#### Scenario: No bed size configured

- **WHEN** a user omits `--bed-x` and `--bed-y`
- **THEN** the system performs no fit check and generates the model without warnings

### Requirement: Warn when bin footprint exceeds print bed

The system SHALL measure the generated model's **actual bounding box** and emit a warning to stderr when any
dimension exceeds the configured build volume — width against bed X, depth against bed Y, and height against the
optional maximum print height — and MUST still generate and export the output file. The model SHALL be evaluated in
its as-generated (printed) orientation; the system SHALL NOT rotate or reorient the model to make it fit, since
doing so could introduce overhang or infill problems.

#### Scenario: Model exceeds the build volume on an axis

- **WHEN** the model's bounding box on X, Y, or Z exceeds the corresponding configured limit
- **THEN** the system prints a warning identifying which axis is exceeded and by how much, then continues to export
  the file and exits zero

#### Scenario: Model fits within the build volume

- **WHEN** the model's bounding box is within the bed (and within the max height when one is configured)
- **THEN** the system generates and exports the file with no warning

#### Scenario: Height is checked only when configured

- **WHEN** `--bed-z` is omitted
- **THEN** the system checks only the X and Y dimensions and does not warn about height

#### Scenario: Warning message is actionable

- **WHEN** a warning is emitted for an oversized model
- **THEN** the message includes the model's dimension and the configured limit so the user can compare them directly

#### Scenario: A model is not rotated to fit

- **WHEN** a model would fit only if rotated, but exceeds a limit in its as-generated orientation
- **THEN** the system still warns that it exceeds the build volume, evaluating the model as-oriented
