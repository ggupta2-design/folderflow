# Folder snapshots

FolderFlow snapshots are portable JSON records of filesystem metadata with optional SHA-256 content checksums. They are designed for change review, backup verification, and automation checks. Creating or comparing a snapshot never moves, deletes, or edits scanned files.

## Capture a baseline

Create a fast metadata baseline:

```bash
folderflow snapshot ~/Documents --recursive --output before.json
```

Add checksums when byte-for-byte content verification matters:

```bash
folderflow snapshot ~/Documents --recursive --checksums --output verified.json
```

Checksum mode reads every included file and can take longer on large folders. The command applies the same hidden-file, exclusion, size, and policy filters as other FolderFlow scans. Use `--force` only when replacing an existing snapshot intentionally.

## Check a live folder

Compare a saved baseline directly with its current folder:

```bash
folderflow check verified.json ~/Documents --recursive
folderflow check verified.json ~/Documents --recursive --json
```

For scheduled scripts or CI, return status 1 when changes are detected:

```bash
folderflow check verified.json ~/Documents --recursive --fail-on-change
```

A metadata baseline produces a metadata check. A checksum baseline automatically hashes the current files and marks the report as SHA-256 verified.

## Compare two saved scans

```bash
folderflow snapshot ~/Documents --recursive --checksums --output after.json
folderflow diff before.json after.json
folderflow diff before.json after.json --json --output changes.json
```

A comparison reports:

- `added`: paths present only in the later snapshot
- `removed`: paths present only in the earlier snapshot
- `modified`: paths with recorded changes and explicit reasons
- `unchanged`: paths with no detected change
- `checksums_compared`: whether both snapshots verified file contents

Modification reasons can include `size`, `modified_time`, `category`, and `content`. FolderFlow does not infer renames. A renamed file appears once under `removed` and once under `added`.

## Snapshot format

Each snapshot contains a schema version, a UTC creation timestamp, a checksum-mode marker, and entries sorted by relative path. Entries contain:

- a portable POSIX-style relative path
- file size in bytes
- nanosecond modification timestamp
- FolderFlow category
- an optional lowercase SHA-256 content checksum

Absolute source-folder paths are intentionally omitted. Snapshot loading rejects unsupported schema versions, absolute paths, parent-directory traversal, duplicate paths, invalid numeric metadata, and malformed checksums. Metadata-only snapshots created by FolderFlow 0.5 remain supported.

## Limitations

Metadata-only snapshots can miss a content change if both size and modification time are preserved. Checksum snapshots close that gap by comparing SHA-256 digests, but they do not prove who changed a file or whether a change was authorized. Keep baselines protected: anyone who can replace both a file and its baseline can hide the difference.
