# ADDED Requirements

## Requirement: CLI-driven STL export

The system SHALL provide a command-line interface that accepts bin-generation parameters and exports STL files suitable
for 3D printing.

### Scenario: Export single STL file from CLI command

- **WHEN** a user runs the CLI with valid parameters and an output target
- **THEN** the system generates the corresponding geometry and writes an STL file to the requested destination

### Scenario: Export with default output destination

- **WHEN** a user runs the CLI with valid parameters and no explicit output file name
- **THEN** the system writes an STL file using a deterministic default naming convention in the default output location

## Requirement: CLI error handling and exit behavior

The system MUST return non-zero exit status for validation or export failures and SHALL emit actionable error text.

### Scenario: Validation failure via CLI

- **WHEN** a user invokes the CLI with invalid parameters
- **THEN** the command exits non-zero and prints validation guidance without producing an STL artifact

### Scenario: Export failure via filesystem constraints

- **WHEN** the CLI cannot write the STL file because of filesystem issues such as a missing directory or denied permission
- **THEN** the command exits non-zero and reports the file output failure cause
