# Contributing

KeeckerOS is currently in repository stabilization and evidence collection.

## Contribution Rules

- Preserve evidence. Do not rewrite, rename, or delete collected artifacts unless a migration plan exists.
- Separate observations from conclusions.
- Back technical claims with evidence: command output, file hash, source path, log, binary metadata, or reproducible analysis.
- Do not add proprietary binaries to public branches until redistribution status is clarified.
- Keep documentation in the numbered `docs/` taxonomy.
- Keep reverse engineering work legal, documented, and scoped to preservation and interoperability.

## Documentation Changes

New technical documents should follow `docs/00-Governance/Documentation-Styleguide.md`.

## Code Changes

Explorer code changes should include a short test or reproducible verification note when possible.

## Commit Hygiene

- Use focused commits.
- Do not mix artifact acquisition, documentation restructuring, and code fixes in the same commit.
- Mention artifact IDs from `docs/03-Evidence/Artifact-Register.md` when changing evidence-related documentation.
