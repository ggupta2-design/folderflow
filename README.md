# FolderFlow

FolderFlow is a local-first command-line tool that organizes cluttered folders safely. It scans files, classifies them by type, previews every proposed move, avoids overwrites, records an undo manifest, and can roll a completed run back.

## Features

- Classifies files with built-in or custom extension categories
- Supports recursive and non-recursive scans
- Skips hidden files and symbolic links by default
- Filters files with relative-path patterns and inclusive size limits
- Loads validated, reusable JSON organization policies
- Finds exact duplicates with SHA-256 content verification
- Produces readable or JSON duplicate reports without deleting files
- Audits storage by file age, size, and category without changing files
- Resolves filename collisions without overwriting files
- Requires explicit confirmation before moving or restoring anything
- Records versioned JSON manifests for auditing and rollback
- Preflights moves and reverses partial work if execution fails
- Uses only the Python standard library at runtime

## Install

```bash
python -m pip install -e ".[dev]"
```

## Preview before organizing

```bash
folderflow plan ~/Downloads
folderflow plan ~/Downloads --recursive --json
```

Planning never changes files. Review the listed source and destination paths before continuing.

## Apply and undo

```bash
folderflow apply ~/Downloads --yes
folderflow rollback ~/Downloads/.folderflow-last-run.json --yes
```

The default manifest is stored inside the organized folder. Supply `--manifest PATH` to keep it elsewhere. Manifests contain absolute local paths and should not be committed publicly.

## Find exact duplicates

Duplicate scans group files only when both their sizes and SHA-256 content digests match. They ignore symbolic links, avoid counting hard links twice, and never delete or move files.

```bash
folderflow duplicates ~/Downloads --recursive
folderflow duplicates ~/Downloads --recursive --json
folderflow duplicates ~/Downloads --minimum-copies 3
```

Save a report for manual review:

```bash
folderflow duplicates ~/Downloads --recursive --json --output duplicates.json
```

FolderFlow refuses to overwrite an existing report unless `--force` is supplied. Reports contain absolute paths, so keep them private. See [SECURITY.md](SECURITY.md) before acting on any duplicate group.

## Audit storage usage

Build a read-only inventory of a folder and summarize the number of files and bytes used by each category:

```bash
folderflow inventory ~/Downloads --recursive
folderflow inventory ~/Downloads --recursive --json
```

Narrow the review to older files and choose an order suited to the task:

```bash
folderflow inventory ~/Downloads --older-than-days 90 --sort oldest
folderflow inventory ~/Downloads --sort largest
```

The age boundary is inclusive. `--sort` accepts `path`, `largest`, or `oldest`. Save the report with the same overwrite protections used by duplicate reports:

```bash
folderflow inventory ~/Downloads --json --output inventory.json
```

An inventory is informational and never deletes or moves files. Modification age alone does not mean a file is safe to remove.

## Custom policies

A policy can replace the built-in category map, ignore relative paths, and set inclusive file-size limits in bytes. Start from [examples/policy.json](examples/policy.json):

```json
{
  "categories": {
    "School": [".pdf", ".docx", ".ipynb"],
    "Photos": [".jpg", ".png"]
  },
  "exclude_patterns": ["drafts/**", "*.tmp"],
  "min_bytes": 1,
  "max_bytes": 104857600
}
```

Validate a policy independently, then use the same rules for previews, confirmed moves, duplicate scans, and storage inventories:

```bash
folderflow validate-policy examples/policy.json
folderflow plan ~/Downloads --config examples/policy.json --recursive
folderflow apply ~/Downloads --config examples/policy.json --recursive --yes
folderflow duplicates ~/Downloads --config examples/policy.json --recursive
folderflow inventory ~/Downloads --config examples/policy.json --recursive
```

CLI filters can extend or override policy filters for a single run:

```bash
folderflow plan ~/Downloads --exclude "private/**" --min-size 100 --max-size 5000000
```

Repeat `--exclude` to add more patterns. CLI size limits take precedence over values from the policy.

## Built-in categories

| Folder | Example extensions |
|---|---|
| Documents | PDF, DOCX, TXT, Markdown |
| Images | JPG, PNG, SVG, HEIC |
| Audio | MP3, WAV, FLAC |
| Video | MP4, MOV, MKV |
| Archives | ZIP, TAR, 7Z |
| Code | Python, JavaScript, TypeScript, SQL |
| Spreadsheets | CSV, XLSX, ODS |
| Other | Files without a recognized extension |

Supplying `categories` in a policy replaces this built-in map. Any extension omitted from the custom map is planned into `Other`.

## Development

```bash
pytest
```

See [SECURITY.md](SECURITY.md) before using FolderFlow on important files.
