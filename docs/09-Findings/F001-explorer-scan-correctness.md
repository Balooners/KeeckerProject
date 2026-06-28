# F001 - Explorer Scan Correctness

Status: Confirmed by audit, Fix Pending

Confidence: Confirmed

## Objective

Record confirmed Explorer scanner issues without changing code during Phase 0 repository stabilization.

## Context

Keecker Explorer is the local network exploration tool under `explorer/`. It is used to probe TCP ports, HTTP endpoints, assets, and generated reports.

## Evidence

- `explorer/probes/tcp.py` defines `probe(host: str, port: int) -> dict`.
- `explorer/scanner.py` calls `if not tcp(host, port):`.
- Non-empty dictionaries are truthy in Python, including dictionaries with `"open": False`.
- `explorer/probes/http.py` references undefined variables inside `download_asset()`.
- `explorer/main.py` has a hardcoded default host.
- `explorer/probes/http.py` and `explorer/analyzers/net_report.py` use cwd-sensitive output paths.

## Analysis

Confirmed issues:

- `tcp()` returns a dictionary but `scanner.py` treats the return value as a boolean.
- `download_asset()` has undefined variables: `endpoint` and `filename` are referenced before local definition in the OPTIONS handling block.
- Exceptions are broadly swallowed in TCP and HTTP probing, which can hide failed scans or incomplete downloads.
- The default target IP is hardcoded as `192.168.1.191`.
- Output paths such as `Path("raw")` and `Path("reports")` depend on the current working directory.

## Conclusions

Explorer scan output may currently be unreliable as evidence. Reports should be treated as provisional until these issues are fixed and verified.

## Open Questions

- Should Explorer write all outputs under `explorer/`, a configured workspace, or a timestamped evidence directory?
- Should scan results include tool version, timestamp, host, retry count, and command line?
- Should generated reports have a schema and validation step?
