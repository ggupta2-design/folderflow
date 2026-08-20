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

## Sensitive information

FolderFlow does not upload files or require credentials. Manifests and duplicate reports can contain absolute local paths, which may reveal usernames and directory names. Local FolderFlow manifests are ignored by Git, and reports should also be excluded before sharing a working directory.

Report security concerns privately through GitHub's security-reporting tools when available. Do not include confidential files, credentials, personal paths, or duplicate reports in a public issue.
