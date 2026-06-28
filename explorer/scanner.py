from probes.tcp import probe as tcp
from probes.http import probe as http

PORTS = [5555, 8008, 8009, 8080, 8443, 9000]


def run(host):

    print()
    print("Keecker Explorer")
    print()

    for port in PORTS:

        if not tcp(host, port):
            print(f"{port} CLOSED")
            continue

        print(f"{port} OPEN")

        if port in [8080, 8443]:

            results = http(host, port)

            for item in results:

                if "error" in item:
                    print(f"   {item['endpoint']:<20} ERROR")
                else:
                    print(
                        f"   {item['endpoint']:<20}"
                        f"{item['status']:>5}"
                        f"{item['length']:>8} bytes"
                    )