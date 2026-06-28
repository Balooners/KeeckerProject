import socket


def probe(host: str, port: int) -> dict:

    result = {
        "open": False,
        "banner": "",
    }

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    try:

        s.connect((host, port))

        result["open"] = True

        try:

            s.send(b"\r\n")

            data = s.recv(4096)

            if data:
                result["banner"] = data.decode(
                    errors="ignore"
                ).strip()

        except Exception:
            pass

    except Exception:
        pass

    finally:
        s.close()

    return result