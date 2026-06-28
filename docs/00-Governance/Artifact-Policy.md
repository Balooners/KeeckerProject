# Artifact Policy

## Objective

Define how KeeckerOS records and handles artifacts collected from Keecker K1 devices.

## Policy

Proprietary binaries, APKs, ODEX files, OAT files, firmware extracts, vendor applications, and other third-party material must not be redistributed publicly until their legal status is clarified.

Local artifacts may be referenced in documentation by:

- filename;
- artifact ID;
- SHA256 hash;
- size;
- source path on device;
- local path;
- acquisition command;
- acquisition date when known;
- notes about provenance and verification.

## Repository Rules

- Public documentation should reference proprietary artifacts by metadata, not by embedding their contents.
- Large binary artifacts should use a storage strategy approved for the project before public release.
- If an artifact must remain local-only, its register entry should set `Redistributable` to `No` or `Unknown`.
- If the legal status is not known, the default status is `Unknown`.
- Do not publish reconstructed proprietary source code.

## Allowed Documentation

The following may be documented:

- hashes and sizes;
- package names;
- source paths;
- acquisition commands;
- file format metadata;
- non-sensitive observations;
- reproducible analysis procedures.

## Not Allowed Until Legal Review

- Public redistribution of proprietary APK, ODEX, OAT, or firmware files.
- Public posting of extracted proprietary source code.
- Public posting of keys, credentials, tokens, or device-specific secrets.

## Canonical Register

The canonical artifact register is `docs/03-Evidence/Artifact-Register.md`.
