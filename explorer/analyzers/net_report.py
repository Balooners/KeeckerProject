from pathlib import Path
import json


def generate(port: int, results: list):

    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)

    normalized = []

    for item in results:

        normalized.append(
            {
                "endpoint": item.get("endpoint"),
                "status": item.get("status"),
                "length": item.get("length"),
                "error": item.get("error"),
                "headers": item.get("headers", {}),
            }
        )

    report = {
        "id": f"NET-{port}",
        "port": port,
        "responses": normalized,
    }

    outfile = report_dir / f"NET-{port}.json"

    outfile.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Report written : {outfile}")