# Cleanup reviews

FolderFlow cleanup reviews combine two independent signals into one read-only report:

- stale files whose modification age meets the selected threshold
- exact duplicates confirmed by SHA-256 content matching

The command never deletes, moves, or renames files.

## Run a review

```bash
folderflow review ~/Downloads --recursive
```

The default stale threshold is 90 days, and duplicate groups require at least two distinct files. Customize either threshold:

```bash
folderflow review ~/Downloads --older-than-days 180 --minimum-copies 3
```

Skip duplicate hashing when only an age-based inventory is needed:

```bash
folderflow review ~/Downloads --older-than-days 365 --no-duplicates
```

## Understand recommendations

Every candidate includes one or both reasons:

- `stale`: the file's recorded modification time is at least the requested age
- `duplicate`: its contents exactly match another file selected as the keeper

Duplicate candidates are marked `verified` because their bytes were compared with SHA-256. Stale-only candidates are marked `review` because age does not establish that a file is unnecessary.

For each duplicate group, FolderFlow sorts paths and treats the first path as the keeper. This choice is deterministic, not a judgment about which copy is most important. Confirm the keeper yourself before removing anything.

## Export a review

```bash
folderflow review ~/Downloads --recursive --json --output cleanup.json
```

Exports use atomic writes and refuse to replace an existing file unless `--force` is supplied. The output file is excluded from its own scan.

## Read the totals

- `total_candidate_bytes` counts every unique candidate once
- `stale_bytes` counts all files matching the age threshold
- `duplicate_reclaimable_bytes` counts bytes recoverable by retaining one file from each exact-match group

These totals overlap when a duplicate is also stale, so they should not be added together.

## Safety boundary

A cleanup review is decision support, not deletion authorization. Modification timestamps can be changed or preserved, duplicate copies can exist for legitimate backup reasons, and filenames can carry important context. Back up important data and inspect every candidate before using separate filesystem tools to remove it.
