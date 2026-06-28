from pathlib import Path

import httpx
from bs4 import BeautifulSoup

ENDPOINTS = [
    "/",
    "/robots.txt",
    "/favicon.ico",
    "/api",
    "/api/status",
    "/status",
    "/config",
    "/version",
    "/health",
]


def download_asset(client, host, port, scheme, asset, outdir):
    """Télécharge une ressource découverte (JS, CSS, image...)."""

    if not asset.startswith("/"):
        return

    try:
        url = f"{scheme}://{host}:{port}{asset}"

        response = client.get(url)

        filename = asset.strip("/").replace("/", "_")

        if filename == "":
            filename = "root"

        (outdir / filename).write_bytes(response.content)

        print(f"      downloaded {asset}")

    except Exception as ex:
        print(f"      failed {asset} : {ex}")


def probe(host: str, port: int):

    scheme = "https" if port == 8443 else "http"

    outdir = Path("raw") / str(port)
    outdir.mkdir(parents=True, exist_ok=True)

    results = []

    with httpx.Client(
        verify=False,
        timeout=5,
        follow_redirects=True
    ) as client:

        for endpoint in ENDPOINTS:

            url = f"{scheme}://{host}:{port}{endpoint}"

            try:

                response = client.get(url)

                filename = endpoint.strip("/")

                if filename == "":
                    filename = "root"

                filename = filename.replace("/", "_")

                (outdir / f"{filename}.txt").write_text(
                    response.text,
                    encoding="utf-8",
                    errors="ignore"
                )

                # Analyse HTML
                if "text/html" in response.headers.get("content-type", ""):

                    soup = BeautifulSoup(response.text, "html.parser")

                    for tag in soup.find_all(["script", "link", "img", "a"]):

                        asset = tag.get("src") or tag.get("href")

                        if asset:

                            print(f"      -> {asset}")

                            download_asset(
                                client,
                                host,
                                port,
                                scheme,
                                asset,
                                outdir
                            )

                results.append(
                    {
                        "endpoint": endpoint,
                        "status": response.status_code,
                        "length": len(response.content),
                    }
                )

            except Exception as ex:

                results.append(
                    {
                        "endpoint": endpoint,
                        "error": str(ex),
                    }
                )

    return results