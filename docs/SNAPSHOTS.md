# Folder snapshots

FolderFlow snapshots are portable JSON records of filesystem metadata. They are designed for change review, backup verification, and automation checks. Creating or comparing a snapshot never moves, deletes, or edits scanned files.

## Capture a baseline

```bash
folderflow snapshot ~/Documents --recursive --output before.json
```

The command applies the same hidden-file, exclusion, size, and policy filters as other FolderFlow scans. Use `--force` only when replacing an existing snapshot intentionally.

## Compare two scans

```bash
folderflow snapshot ~/Documents --recursive --output after.json
folderflow diff before.json after.json
folderflow diff before.json after.json --json --output changes.json
```

A comparison reports:

- `added`: paths present only in the later snapshot
- `removed`: paths present only in the earlier snapshot
- `modified`: paths whose size, modification timestamp, or category changed
- `unchanged`: paths with identical recorded metadata

FolderFlow does not infer renames. A renamed file appears once under `removed` and once under `added`.

## Snapshot format

Each snapshot contains a schema version, a UTC creation timestamp, and entries sorted by relative path. Entries contain:

- a portable POSIX-style relative path
- file size in bytes
- nanosecond modification timestamp
- FolderFlow category

Absolute source-folder paths are intentionally omitted. Snapshot loading rejects unsupported schema versions, absolute paths, parent-directory traversal, duplicate paths, and invalid numeric metadata.

## Limitations

Snapshots compare metadata rather than file contents. A file can theoretically change without detection if both its size and recorded modification time are preserved. Use FolderFlow's SHA-256 duplicate scanner when content identity matters.
