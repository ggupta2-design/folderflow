# FolderFlow

FolderFlow is a local-first command-line tool that organizes cluttered folders safely.

It scans files, classifies them by type, previews every proposed move, avoids overwriting existing files, records an undo manifest, and can roll a completed organization run back.

## Planned first release

- Extension-based file classification
- Recursive and non-recursive scanning
- Dry-run organization plans
- Collision-safe destination names
- JSON manifests for auditing and rollback
- A scriptable CLI with no external runtime dependencies

FolderFlow never uploads files and does not require credentials.
