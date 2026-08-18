# Security

FolderFlow performs local filesystem moves, so review every plan before applying it.

## Safe use

- Run `folderflow plan PATH` before `folderflow apply PATH --yes`.
- Keep the generated manifest until the result has been reviewed.
- Back up irreplaceable files before any bulk organization.
- Do not edit a manifest before rollback.
- FolderFlow refuses destination overwrites and skips symbolic links by default.

## Sensitive information

FolderFlow does not upload files or require credentials. Manifests contain absolute local paths, which can reveal usernames and directory names, so `.folderflow*.json` files are ignored by Git.

Report security concerns privately through GitHub's security-reporting tools when available. Do not include confidential files, credentials, or personal paths in a public issue.
