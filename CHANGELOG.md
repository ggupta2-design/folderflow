# Changelog

## 0.7.0

- Added unified cleanup reviews for stale and exact-duplicate files.
- Added deterministic keeper selection for duplicate groups.
- Added explicit stale and duplicate recommendation reasons.
- Distinguished SHA-256-verified duplicates from age-based review signals.
- Merged overlapping signals without duplicating candidate totals.
- Added configurable age and duplicate-copy thresholds.
- Added a `--no-duplicates` mode for metadata-only reviews.
- Added readable and machine-readable review formats.
- Added atomic exports with output self-exclusion and policy support.
- Documented keeper limitations, overlapping totals, and deletion boundaries.
- Added model, summary, formatting, CLI, export, and policy regression coverage.

## 0.6.0

- Added optional SHA-256 content checksums to portable snapshots.
- Preserved compatibility with FolderFlow 0.5 metadata snapshots.
- Added strict lowercase SHA-256 validation.
- Added explicit size, timestamp, category, and content change reasons.
- Marked reports as checksum-verified or metadata-only.
- Added direct saved-baseline checks against live folders.
- Added automation-friendly `--fail-on-change` exit statuses.
- Excluded baseline and output files from live comparisons.
- Documented checksum performance, privacy, and trust boundaries.
- Added checksum, migration, diff, formatting, live-check, and CLI coverage.

## 0.5.0

- Added portable, versioned folder metadata snapshots.
- Stored sorted relative paths instead of absolute source-folder paths.
- Added strict snapshot schema and path-safety validation.
- Added deterministic snapshot JSON round trips.
- Added comparisons for added, removed, modified, and unchanged files.
- Added readable and machine-readable change reports.
- Added `snapshot` and `diff` CLI workflows.
- Added atomic output handling with overwrite protection.
- Documented metadata-comparison limitations and privacy boundaries.
- Added model, validation, comparison, formatting, and CLI regression coverage.

## 0.4.0

- Added read-only file inventories with size, modification age, and category metadata.
- Added inclusive age filtering for focused stale-file reviews.
- Added category-level file counts and storage totals.
- Added readable and machine-readable inventory formats.
- Added deterministic path, largest-first, and oldest-first ordering.
- Added an `inventory` CLI command that reuses policy and scan filters.
- Added atomic inventory report exports with overwrite protection.
- Prevented an existing output report from appearing in its own inventory.
- Documented report privacy and the limits of age-based cleanup decisions.
- Added unit, formatting, CLI, sorting, and export regression coverage.

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
