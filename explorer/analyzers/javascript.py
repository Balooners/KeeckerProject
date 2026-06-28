from pathlib import Path
import re


PATTERNS = {
    "REST": [
        r'["\'](\/api\/[^"\']+)["\']',
        r'["\'](\/v[0-9]+\/[^"\']+)["\']',
    ],
    "FETCH": [
        r'fetch\(\s*["\']([^"\']+)["\']',
    ],
    "AXIOS": [
        r'axios\.(?:get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']',
    ],
    "WEBSOCKET": [
        r'wss?:\/\/[^"\']+',
        r'new\s+WebSocket\(\s*["\']([^"\']+)["\']',
    ],
    "CAST": [
        r'googlecast',
        r'cast',
        r'dial',
        r'cast_receiver',
        r'cast_sender',
        r'chrome\.cast',
        r'__onGCastApiAvailable',
    ],
    "URL": [
        r'https?:\/\/[^\s"\'`]+',
    ],
}


def _extract(text: str, patterns: list[str]) -> list[str]:
    values = set()

    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        for match in matches:
            if isinstance(match, tuple):
                match = match[0]

            values.add(match.strip())

    return sorted(values)


def analyze(js_file: Path):

    print()
    print("=" * 60)
    print(f"JavaScript Analysis : {js_file.name}")
    print("=" * 60)

    text = js_file.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    for section, patterns in PATTERNS.items():

        print()
        print(f"[{section}]")

        values = _extract(text, patterns)

        if not values:
            print("  none")
            continue

        for value in values:
            print(" ", value)