from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from analyzers.javascript import analyze
from analyzers.net_report import generate

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
    "/apps",
    "/apps/",
    "/apps/YouTube",
    "/apps/Chrome",
    "/apps/Backdrop",
    "/setup/eureka_info",
    "/setup/eureka_info?options=detail",
    "/setup/icon",
    "/ssdp/device-desc.xml",
    "/device.description.xml",
    "/setup/icon.png",
    "/setup/device_info",
    "/setup/device_info.json",
    "/setup/deviceinfo",
    "/setup/scan_results",
    "/setup/network",
    "/setup/reboot",
    "/setup/status",
    "/setup/config",
    "/setup/bluetooth",
    "/setup/wifi",
    "/ssdp/device-desc.xml",
    "/description.xml",
    "/rootDesc.xml",
]


def download_asset(client, host, port, scheme, asset, outdir):
    """Télécharge une ressource découverte (JS, CSS, image...)."""

    if not asset.startswith("/"):
        return

    try:
        url = f"{scheme}://{host}:{port}{asset}"

        response = client.get(url)
        try:
            options = client.options(url)

            if options.status_code != 404:
                print(f"      OPTIONS {endpoint} -> {options.status_code}")

                (outdir / f"{filename}_OPTIONS.txt").write_text(
                    "\n".join(
                        f"{k}: {v}"
                        for k, v in options.headers.items()
                    ),
                    encoding="utf-8",
                )

        except Exception:
            pass

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

                filename = (
                    filename
                    .replace("/", "_")
                    .replace("\\", "_")
                    .replace("?", "_")
                    .replace("=", "_")
                    .replace("&", "_")
                    .replace(":", "_")
                )

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
                        "headers": dict(response.headers),
                    }
                )

            except Exception as ex:

                results.append(
                    {
                        "endpoint": endpoint,
                        "error": str(ex),
                    }
                )

    for js in outdir.glob("*.js"):
        analyze(js)

    generate(port, results)

    return results