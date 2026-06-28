import socket

def probe(host: str, port: int) -> bool:
    s = socket.socket()
    s.settimeout(1)

    try:
        s.connect((host, port))
        s.close()
        return True
    except:
        return False