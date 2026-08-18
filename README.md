# FolderFlow

FolderFlow is a local-first command-line tool that organizes cluttered folders safely. It scans files, classifies them by type, previews every proposed move, avoids overwrites, records an undo manifest, and can roll a completed run back.

## Features

- Classifies documents, images, audio, video, archives, code, and spreadsheets
- Supports recursive and non-recursive scans
- Skips hidden files and symbolic links by default
- Produces readable or JSON organization previews
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

## Categories

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

## Development

```bash
pytest
```

See [SECURITY.md](SECURITY.md) before using FolderFlow on important files.
