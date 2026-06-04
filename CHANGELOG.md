# Changelog

## Unreleased
- Fixed ABC category assignment for dominant articles that individually cross the 80% threshold.
- Added stricter validation for empty inputs, duplicate month numbers, and negative monthly movement values.
- Refactored monthly coercion, ABC column construction, and summary generation into focused helper functions.
- Removed import-time logging configuration from the CLI module.
- Separated plot saving from interactive plot display.

## 0.1.0
- Refactored the project from a single script into an installable package.
- Added a stable CLI and preserved the legacy script as a wrapper.
- Added input validation, explicit configuration, and dependency-safe help paths.
- Added repository documentation, contributor guidance, CI updates, and package metadata.
