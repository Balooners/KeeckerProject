# Documentation Style Guide

## Objective

Keep KeeckerOS documentation reproducible, evidence-backed, and maintainable.

## Required Sections

Technical analysis documents should include:

- Objective
- Context
- Evidence
- Analysis
- Conclusions
- Open Questions

Short index and README files may omit these sections.

## Confidence Levels

Use one of these levels for technical claims:

- Confirmed: directly supported by evidence such as command output, hash, binary metadata, captured response, or reproducible observation.
- Probable: supported by multiple signals but not yet fully proven.
- Hypothesis: plausible interpretation that needs more evidence.

## Evidence Rules

- Link claims to an artifact ID, command output, log, screenshot, capture, source path, or hash.
- Distinguish observation from interpretation.
- Do not overwrite historical notes to make them cleaner; create consolidated findings instead.
- Preserve uncertainty explicitly.

## Naming Rules

- Canonical documentation folders use numbered kebab-case names under `docs/`.
- Findings use stable IDs such as `F001-short-title.md`.
- Evidence entries use stable IDs such as `ART-0001`.
- Prefer ASCII filenames.
- Avoid spaces in filenames.

## Status Labels

Recommended status labels:

- Draft
- In Review
- Confirmed
- Fix Pending
- Superseded
- Archived
