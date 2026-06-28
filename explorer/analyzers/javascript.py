from pathlib import Path
import re


PATTERNS = {
    "REST": r'["\'](\/api\/[^"\']+)["\']',
    "FETCH": r'fetch\(["\']([^"\']+)["\']',
    "AXIOS": r'axios\.[a-z]+\(["\']([^"\']+)["\']',
    "WEBSOCKET": r'wss?:\/\/[^"\']+',
    "CAST": r'cast|googlecast|dial',
}


def analyze(js_file: Path):

    print()
    print("=" * 60)
    print(f"JavaScript Analysis : {js_file.name}")
    print("=" * 60)

    text = js_file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    for name, pattern in PATTERNS.items():

        print()
        print(f"[{name}]")

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not matches:

            print("  none")
            continue

        for value in sorted(set(matches)):
            print(" ", value)