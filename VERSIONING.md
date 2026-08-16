# Versioning

This project follows a versioning pattern similar to [Semantic Versioning](https://semver.org/) (SemVer) for managing releases.

Versions are tracked at two levels: the **repository** as a whole, and each **module project** inside it.

## Table of Contents

- [Versioning](#versioning)
  - [Table of Contents](#table-of-contents)
  - [Versioning Scopes](#versioning-scopes)
    - [Repository releases — `MAJOR.MINOR`](#repository-releases--majorminor)
    - [Module projects — `MAJOR.MINOR.PATCH`](#module-projects--majorminorpatch)
  - [Examples](#examples)
  - [Release Process](#release-process)
    - [Typical Steps](#typical-steps)
  - [Pre-release Versions](#pre-release-versions)
  - [Viewing Tags \& Differences](#viewing-tags--differences)
  - [Questions or Issues?](#questions-or-issues)

## Versioning Scopes

| Scope | Format | Example | Where it lives |
| ----- | ------ | ------- | -------------- |
| Repository release | `MAJOR.MINOR` | `v2.0` | Git tag, `CHANGELOG.md`, GitHub release |
| Module project | `MAJOR.MINOR.PATCH` | `1.4.2` | The module's own manifest |

### Repository releases — `MAJOR.MINOR`

The repository is a workshop, not a library. A release is an **edition** of that workshop, so it uses a two-part version.

- **MAJOR** – A new workshop. Rebuilt content, a restructured repository, or any change that invalidates the previous edition's instructions.
- **MINOR** – Improvements within the current edition: new modules, corrections, refreshed dependencies.

There is no patch component. A workshop edition is either current or superseded, and a typo fix does not warrant its own release — it simply lands on the current edition.

### Module projects — `MAJOR.MINOR.PATCH`

Each module inside the repository is real software with its own dependencies and lifecycle, so it uses full SemVer.

| Module | Manifest |
| ------ | -------- |
| `app/` | `pyproject.toml` |
| `lab/` | `pyproject.toml` |
| `client/streamlit/` | `pyproject.toml` |
| `client/web/` | `package.json` |
| `website/` | `package.json` |

- **MAJOR** – Incompatible API changes or major breaking updates
- **MINOR** – Backward-compatible functionality and feature additions
- **PATCH** – Backward-compatible bug fixes and small improvements

Module versions are recorded in their manifests and are **not** tagged individually. The repository tag is the release; module versions describe the state of each part within it.

> [!IMPORTANT]
> `package.json` requires a full three-part SemVer string — npm rejects `2.0`. The repository's `MAJOR.MINOR` version therefore lives only in Git tags, the changelog and GitHub releases, never in a manifest.

## Examples

Repository releases:

| Version | Meaning |
| ------- | ------- |
| `v1.0` | First public edition of the workshop |
| `v1.1` | New module or corrections within that edition |
| `v2.0` | A new workshop — rebuilt content and structure |

Module projects:

| Version | Meaning |
| ------- | ------- |
| `0.1.0` | Early development |
| `1.0.0` | First stable version of the module |
| `1.0.1` | Bug fix |
| `1.1.0` | New non-breaking feature |
| `2.0.0` | Breaking change |

## Release Process

All notable changes are documented in the [CHANGELOG.md](CHANGELOG.md) file.

### Typical Steps

1. Complete all features and fixes planned for the release
2. Update the `CHANGELOG.md` with categorized entries:  
   - **Added**, **Changed**, **Fixed**, **Removed**
3. Bump the version in each module manifest that changed (`pyproject.toml`, `package.json`, and any lock files)
4. Commit changes with a version-related message (e.g. `chore(repo): Release v2.0`)
5. Tag the release:

   ```bash
   git tag v2.0
   git push origin v2.0
   ```

6. (Optional) Create a GitHub release and paste the relevant changelog section

## Pre-release Versions

For beta or release candidates, we use suffixes at either scope:

- `v2.0-rc.1` – Repository release candidate
- `1.2.0-beta.1` – Module beta release

These versions are intended for testing and may not be fully stable.

## Viewing Tags & Differences

List all version tags:

```bash
git tag
```

View differences between versions:

```bash
git log v1.0..v2.0
```

## Questions or Issues?

If you have questions about the versioning strategy or encounter version-related problems, feel free to open an issue on the [GitHub repository](https://github.com/dileepadev/microsoft-agent-framework-workshop/issues).
