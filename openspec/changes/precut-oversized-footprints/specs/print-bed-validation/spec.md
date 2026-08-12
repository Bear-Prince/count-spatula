# print-bed-validation Specification

## MODIFIED Requirements

### Requirement: Warn when bin footprint exceeds print bed

The system SHALL measure the generated model's **actual bounding box** and emit a warning to stderr when any
dimension exceeds the configured build volume - width against bed X, depth against bed Y, and height against the
maximum print height (Z) - and MUST still generate and export the output file. The model SHALL be evaluated in
its as-generated (printed) orientation; the system SHALL NOT rotate or reorient the model to make it fit, since
doing so could introduce overhang or infill problems. Where the overflow is on X or Y, the warning SHALL name
`--split` as the available remedy; a Z-axis overflow SHALL NOT suggest it, since splitting does not apply to
that axis.

#### Scenario: Model exceeds the build volume on an axis

- **WHEN** the model's bounding box on X, Y, or Z exceeds the corresponding configured limit
- **THEN** the system prints a warning identifying which axis is exceeded and by how much, then continues to export
  the file and exits zero

#### Scenario: Model fits within the build volume

- **WHEN** the model's bounding box is within the bed (and within the max height when one is configured)
- **THEN** the system generates and exports the file with no warning

#### Scenario: Warning message is actionable

- **WHEN** a warning is emitted for an oversized model
- **THEN** the message includes the model's dimension and the configured limit so the user can compare them directly

#### Scenario: Horizontal overflow names the split remedy

- **WHEN** a warning is emitted because the model exceeds the bed on X or Y
- **THEN** the message names `--split` as the way to resolve it

#### Scenario: Height overflow does not suggest splitting

- **WHEN** a warning is emitted because the model exceeds the maximum print height
- **THEN** the message does not name `--split`, since splitting does not apply to the Z axis

#### Scenario: A model is not rotated to fit

- **WHEN** a model would fit only if rotated, but exceeds a limit in its as-generated orientation
- **THEN** the system still warns that it exceeds the build volume, evaluating the model as-oriented
