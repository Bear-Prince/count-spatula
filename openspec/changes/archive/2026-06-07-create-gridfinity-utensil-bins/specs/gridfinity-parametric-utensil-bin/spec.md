# ADDED Requirements

## Requirement: Parametric Gridfinity utensil bin geometry

The system SHALL generate kitchen utensil bin geometry that is compatible with the Gridfinity standard from validated
user-supplied parameters and documented defaults.

### Scenario: Generate geometry from explicit valid parameters

- **WHEN** a user provides valid Gridfinity-aligned parameters for bin size and geometry values
- **THEN** the system produces a geometry model that reflects those parameters without runtime geometry errors

### Scenario: Generate geometry from defaults

- **WHEN** a user omits optional parameters
- **THEN** the system applies documented defaults and produces a valid Gridfinity-compatible utensil bin geometry

## Requirement: Parameter validation for printable geometry

The system MUST validate user parameters before geometry construction and reject values that are outside supported,
printable ranges with actionable error messages.

### Scenario: Reject unsupported parameter values

- **WHEN** a user provides parameter values outside supported ranges
- **THEN** the system refuses geometry generation and reports which parameters are invalid and why

### Scenario: Reject incompatible parameter combinations

- **WHEN** a user provides a combination of values that cannot produce valid printable geometry
- **THEN** the system refuses generation and returns a clear validation error describing the conflicting inputs
