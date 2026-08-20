# Changelog

## 0.3.0

- Added exact duplicate discovery using size grouping and SHA-256 verification.
- Added reclaimable-byte totals and deterministic group ordering.
- Avoided counting hard links to the same underlying file more than once.
- Added readable and machine-readable duplicate reports.
- Added a non-destructive `duplicates` CLI command.
- Added configurable minimum-copy thresholds.
- Added atomic report exports with overwrite protection.
- Reused policy exclusions and size filters for duplicate scans.
- Documented manual review and report privacy safeguards.
- Added unit, CLI, formatting, and report-export regression coverage.

## 0.2.0

- Added validated JSON organization policies.
- Added custom extension-to-category mappings.
- Added relative-path exclusion patterns.
- Added inclusive minimum and maximum file-size filters.
- Added CLI overrides for exclusions and size bounds.
- Added a standalone `validate-policy` command.
- Added an example policy and end-to-end policy CLI coverage.
- Preserved preview-first, confirmation, manifest, and rollback safeguards.

## 0.1.0

- Created an installable, dependency-free Python CLI.
- Added extension-based file classification.
- Added recursive scanning with hidden-file and symlink safeguards.
- Added collision-safe organization planning.
- Added readable and JSON dry-run previews.
- Added confirmed move execution with overwrite protection.
- Added versioned manifests and rollback support.
- Added regression tests and GitHub Actions.
- Documented safe operation and sensitive-path handling.
