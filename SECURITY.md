# Security

FolderFlow performs local filesystem moves, so review every plan before applying it.

## Safe use

- Run `folderflow plan PATH` before `folderflow apply PATH --yes`.
- Keep the generated manifest until the result has been reviewed.
- Back up irreplaceable files before any bulk organization.
- Do not edit a manifest before rollback.
- FolderFlow refuses destination overwrites and skips symbolic links by default.

## Duplicate reports

The `duplicates` command is read-only: it hashes file contents and reports exact matches but never deletes, moves, or replaces scanned files. Files with equal sizes are not considered duplicates unless their SHA-256 digests also match. Hard links to the same underlying file are counted once.

Review duplicate groups manually before removing anything. FolderFlow intentionally does not provide automatic duplicate deletion. Report exports contain absolute local paths and content digests; store them privately and use `--force` only when you intend to replace an existing report.

## Storage inventories

The `inventory` command is also read-only. It reads file sizes and modification times, classifies paths, and generates summaries without opening file contents or changing filesystem metadata. Age filters are meant to narrow manual review; an old modification time does not prove a file is unnecessary.

Inventory exports contain absolute paths, sizes, categories, and modification timestamps. Treat them as private operational data and review them before sharing.

## Snapshot safety

Snapshot files contain relative paths, sizes, categories, and modification timestamps. Relative paths reduce accidental disclosure of usernames and source-folder locations, but filenames can still contain private information. Keep snapshots and exported comparisons private unless their contents have been reviewed.

Snapshot comparison uses metadata and is not a cryptographic integrity check. It must not be used as proof that file contents are unchanged. Snapshot loading rejects absolute paths, parent traversal, duplicate paths, invalid numeric fields, and unsupported schema versions.

## Sensitive information

FolderFlow does not upload files or require credentials. Manifests, duplicate reports, and inventory reports can contain absolute local paths, which may reveal usernames and directory names. Local FolderFlow manifests are ignored by Git, and reports should also be excluded before sharing a working directory.

Report security concerns privately through GitHub's security-reporting tools when available. Do not include confidential files, credentials, personal paths, duplicate reports, or snapshots in a public issue.
