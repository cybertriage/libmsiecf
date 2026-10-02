# libmsiecf for Cyber Triage

This fork builds the `msiecfexport` that Cyber Triage runs to parse Internet
Explorer `index.dat` files. It replaces Pasco2 (CT-11834).

Work happens on the `ct` branch. `main` tracks upstream
[libyal/libmsiecf](https://github.com/libyal/libmsiecf) unchanged.

## What differs from upstream

- `msiecfexport` skips an item it cannot read and carries on. Upstream stops at
  the first bad record, so every later record is lost.
- A double free on partial recovered URL records is fixed.
- The `-m` option works again. Upstream registers it as `-l`.
- An "Unable to export item" message always starts on its own line, so a
  half-exported item cannot run into it.
- The libyal dependencies are pinned in `ct/dependencies.txt`.
  `synclibs.sh` and `synclibs.ps1` check out those tags, not the latest ones.
- `.github/workflows/ct_release.yml` builds the binaries Cyber Triage ships.

Each change is its own commit, so each can be offered upstream on its own.

## Getting the binaries

Do not build locally. Download a release from this repository's Releases page.
Each release has:

| File | Contents |
|---|---|
| `msiecfexport-<tag>-windows-x64.zip` | `msiecfexport.exe`, `libmsiecf.dll`, `vcruntime140.dll` |
| `msiecfexport-<tag>-linux-x86_64.tar.gz` | `msiecfexport`, statically linked |
| `SHA256SUMS` | SHA-256 of both archives |

Both archives also carry `COPYING`, `COPYING.LESSER`, `dependencies.txt` and a
`SOURCE.txt` naming the exact source commit and build.

The Windows build needs the Universal C Runtime, which ships with Windows 10 and
later.

Every push to `ct` builds the same archives and keeps them as workflow
artifacts for the run. Only a tag publishes a release.

## Making a release

1. Make sure the `ct_release` workflow passes on `ct`.
2. Tag the commit `ct-<upstream version>.<n>`, for example `ct-20260924.1`.
   The upstream version is the `AC_INIT` version in `configure.ac`.
3. Push the tag. The workflow publishes the release.

Never move or reuse a tag. Cyber Triage pins a release by its SHA-256.

## Updating a dependency

Change its line in `ct/dependencies.txt` in its own commit, then release.

## Updating from upstream

```
git fetch upstream
git switch main && git merge --ff-only upstream/main && git push origin main
git switch ct && git rebase main
```

Then check that the `ct_release` workflow passes, and release.

## Licence

LGPL-3.0-or-later, the same as upstream. The source for every release is this
repository at the commit named in its `SOURCE.txt`.
