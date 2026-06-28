# Migration Report - 2026-06-28

## Objective

Document Phase 0 repository stabilization changes.

## Scope

Documentation and repository hygiene only. No reverse engineering was performed.

## Created Files

Repository root:

- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `ROADMAP.md`
- `AGENTS.md`

Governance:

- `docs/00-Governance/Artifact-Policy.md`
- `docs/00-Governance/Documentation-Styleguide.md`
- `docs/00-Governance/Migration-Report-2026-06-28.md`

Evidence:

- `docs/03-Evidence/Artifact-Register.md`

Findings:

- `docs/09-Findings/F001-explorer-scan-correctness.md`

Archive navigation:

- `docs/90-Archive/legacy-docs/README.md`
- `docs/90-Archive/legacy-docs/INDEX.md`

## Updated Files

- `docs/INDEX.md`
- `docs/00-Governance/INDEX.md`
- `docs/03-Evidence/INDEX.md`
- `docs/09-Findings/INDEX.md`
- `docs/90-Archive/INDEX.md`

## Moved Files

Legacy duplicate documentation folders were moved under `docs/90-Archive/legacy-docs/`.

| From | To |
|---|---|
| `docs/Android/README.md` | `docs/90-Archive/legacy-docs/Android/README.md` |
| `docs/Android/INDEX.md` | `docs/90-Archive/legacy-docs/Android/INDEX.md` |
| `docs/APK/README.md` | `docs/90-Archive/legacy-docs/APK/README.md` |
| `docs/APK/INDEX.md` | `docs/90-Archive/legacy-docs/APK/INDEX.md` |
| `docs/Architecture/README.md` | `docs/90-Archive/legacy-docs/Architecture/README.md` |
| `docs/Architecture/INDEX.md` | `docs/90-Archive/legacy-docs/Architecture/INDEX.md` |
| `docs/Binder/README.md` | `docs/90-Archive/legacy-docs/Binder/README.md` |
| `docs/Binder/INDEX.md` | `docs/90-Archive/legacy-docs/Binder/INDEX.md` |
| `docs/Hardware/README.md` | `docs/90-Archive/legacy-docs/Hardware/README.md` |
| `docs/Hardware/INDEX.md` | `docs/90-Archive/legacy-docs/Hardware/INDEX.md` |
| `docs/Native/README.md` | `docs/90-Archive/legacy-docs/Native/README.md` |
| `docs/Native/INDEX.md` | `docs/90-Archive/legacy-docs/Native/INDEX.md` |
| `docs/OTA/README.md` | `docs/90-Archive/legacy-docs/OTA/README.md` |
| `docs/OTA/INDEX.md` | `docs/90-Archive/legacy-docs/OTA/INDEX.md` |
| `docs/ReverseEngineering/README.md` | `docs/90-Archive/legacy-docs/ReverseEngineering/README.md` |
| `docs/ReverseEngineering/INDEX.md` | `docs/90-Archive/legacy-docs/ReverseEngineering/INDEX.md` |

## Removed Empty Folders

The following empty legacy folder shells were removed after their files were archived:

- `docs/Android/`
- `docs/APK/`
- `docs/Architecture/`
- `docs/Binder/`
- `docs/Hardware/`
- `docs/Native/`
- `docs/OTA/`
- `docs/ReverseEngineering/`

## Taxonomy Decision

The numbered documentation folders are canonical:

- `docs/00-Governance/`
- `docs/01-Architecture/`
- `docs/02-Acquisition/`
- `docs/03-Evidence/`
- `docs/04-Analysis/`
- `docs/05-Interfaces/`
- `docs/06-Firmware/`
- `docs/07-Hardware/`
- `docs/08-Network/`
- `docs/09-Findings/`
- `docs/10-Operations/`
- `docs/90-Archive/`

## Unresolved Issues

- Final open-source license is undecided.
- Public redistribution status of proprietary APK, ODEX, OAT, and firmware artifacts is unknown.
- APK source paths, sizes, and SHA256 hashes are not yet normalized in the artifact register.
- `firmware/boot-oat` is a local file whose name differs from the source filename `boot.oat`.
- Explorer correctness issues are documented in `docs/09-Findings/F001-explorer-scan-correctness.md` but intentionally not fixed in Phase 0.
- Existing modified files `README.md` and `docs/DISCOVERIES.md` predate this phase and were not normalized here.
