# AGENTS.md

# KeeckerOS — AI Collaboration Guide

This repository is a long-term reverse engineering and preservation project dedicated to the Keecker K1 robot.

The objective is to produce the most complete technical documentation available for the Keecker platform while preparing the future open-source KeeckerOS software stack.

---

# Core Principles

The repository is the single source of truth.

Documentation is as important as source code.

Every change must improve:

* maintainability
* reproducibility
* traceability
* documentation quality

This repository is expected to remain maintainable for at least ten years.

---

# First Actions

Before proposing any modification:

1. Read README.md
2. Read CHANGELOG.md
3. Read SESSION_STATE.md
4. Read handbook/
5. Read docs/
6. Check `git status --short`

Never recreate documentation that already exists.

Always improve existing documentation first.

---

# Reverse Engineering Rules

Default mode is read-only.

Do not propose:

* rooting
* firmware flashing
* destructive operations

unless explicitly requested.

Every technical statement must be supported by evidence.

Unknown information must never be presented as fact.

---

# Documentation Rules

Evidence and analysis are separate.

Evidence contains:

* ADB outputs
* APKs
* ODEX/OAT
* hashes
* manifests
* binaries
* logs
* captures

Analysis contains:

* architecture
* interpretation
* hypotheses
* conclusions

Always specify confidence:

* ✅ Confirmed
* 🟡 Probable
* 🔴 Hypothesis

---

# Repository Rules

Treat numbered `docs/` folders as canonical.

Treat `docs/90-Archive/` as historical documentation.

Do not duplicate folder structures.

Do not duplicate documentation.

Prefer improving existing documents.

---

# Artifact Rules

Do not redistribute proprietary firmware or binaries.

Reference artifacts using:

* filename
* SHA256
* acquisition command
* original device path

Whenever possible, link to the Artifact Register.

---

# Engineering Philosophy

Think before acting.

Read before writing.

Understand before modifying.

Incremental improvements are preferred over large rewrites.

Repository consistency is more important than speed.

---

# Current Project Phase

Android platform acquisition has been completed.

Current focus:

* ODEX reconstruction
* Binder analysis
* JNI mapping
* Native library analysis
* Robot architecture reconstruction

Network discovery and APK acquisition should not be repeated unless explicitly requested.

---

# Goal

Every contribution should make KeeckerOS a better engineering reference for the community and help preserve the original Keecker platform for future developers.
