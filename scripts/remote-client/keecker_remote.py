#!/usr/bin/env python3
"""Minimal open client for the Keecker K1 companion-app protocol.

Protocol reference: docs/05-Interfaces/remote-app-protocol.md
  - discovery: mDNS service `_keecker._tcp`, TXT fields uuid / v / vn
  - transport: WebSocket ws://<robot>:8080/remote/keecker.ws, one protocol message per binary frame,
    single-byte 0xAA frames are keep-alive pings echoed by the robot
  - handshake: AuthMessage in clear (our public key, device id, user id), the robot answers with
    ServiceVersionMessage then AuthMessage (its public key) or AuthMessage (error code)
  - after the handshake: every frame is nonce(24) || crypto_box(KeeckerMessage)

Scope: read status and drive the projector LED and tilt. This client never sends movement commands.
Protobuf messages are encoded by hand from the public field numbers; no Keecker file is copied here.
"""

import argparse
import base64
import json
import os
import sys
import threading
import time
import uuid
from pathlib import Path

from nacl.public import Box, PrivateKey, PublicKey

DEFAULT_PORT = 8080
WS_PATH = '/remote/keecker.ws'
SERVICE_TYPE = '_keecker._tcp.local.'
PING = b'\xaa'
KEEPALIVE_S = 5
PLATFORM = 'keeckeros-test-client'
VERSION_CODE = 20003  # same protocol level as the last official app (2.0.3)
STATE_FILE = Path.home() / '.keeckeros' / 'remote-client.json'


# ---------------------------------------------------------------- protobuf (proto2 wire format)

def _varint(n):
    n &= (1 << 64) - 1
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _read_varint(data, i):
    shift = result = 0
    while True:
        b = data[i]
        i += 1
        result |= (b & 0x7F) << shift
        if not b & 0x80:
            return result, i
        shift += 7


def encode(fields):
    """Encode [(field_number, value)], value being bool, int, str, bytes or None (skipped)."""
    out = bytearray()
    for num, value in fields:
        if value is None:
            continue
        if isinstance(value, bool):
            out += _varint(num << 3) + _varint(int(value))
        elif isinstance(value, int):
            out += _varint(num << 3) + _varint(value)
        else:
            raw = value.encode() if isinstance(value, str) else bytes(value)
            out += _varint(num << 3 | 2) + _varint(len(raw)) + raw
    return bytes(out)


def decode(data):
    """Decode a message into {field_number: [values]}; varints as int, length-delimited as bytes."""
    fields, i = {}, 0
    while i < len(data):
        key, i = _read_varint(data, i)
        num, wire = key >> 3, key & 7
        if wire == 0:
            value, i = _read_varint(data, i)
            if value >= 1 << 63:
                value -= 1 << 64
        elif wire == 2:
            size, i = _read_varint(data, i)
            value, i = data[i:i + size], i + size
        elif wire == 5:
            value, i = int.from_bytes(data[i:i + 4], 'little'), i + 4
        elif wire == 1:
            value, i = int.from_bytes(data[i:i + 8], 'little'), i + 8
        else:
            raise ValueError(f'unsupported wire type {wire}')
        fields.setdefault(num, []).append(value)
    return fields


AUTH_ERRORS = {
    0: 'INCORRECT_AUTH_MESSAGE', 1: 'UNKNOWN_USER', 2: 'UNAUTHORIZED_USER_FOR_CONNECTION_TYPE',
    3: 'INCORRECT_PUBLIC_KEY_AND_DEVICE_ID', 4: 'INCORRECT_TOKEN', 5: 'INCORRECT_KEECKER_PUBLIC_KEY',
    6: 'IN_SETUP_ALREADY_HAVE_CONNECTION', 7: 'UNHANDLED_EXCEPTION', 8: 'USER_ACCESS_HAS_NOT_STARTED',
    9: 'USER_ACCESS_HAS_FINISHED', 10: 'PERSISTANCE_ERROR', 11: 'FORCE_UPGRADE',
}
R_PROJECTOR_STATUS = {
    1: ('ledOn', 'bool'), 2: ('keystone', 'int'), 3: ('autoKeystone', 'bool'), 4: ('zoom', 'int'),
    5: ('brightness', 'int'), 6: ('contrast', 'int'),
    7: ('displayMode', {0: 'BRIGHTEST', 1: 'VIVID', 2: 'MOVIE', 3: 'PICTURE', 4: 'USER'}),
    8: ('displayPosition', {0: 'FRONT_TABLE', 1: 'FRONT_CEILING', 2: 'REAR_TABLE', 3: 'REAR_CEILING'}),
    9: ('aspectRatio', {0: 'RAUTO', 1: 'R4_3', 2: 'R16_9', 3: 'R16_10'}),
    13: ('focus', 'int'), 14: ('autoFocus', 'bool'), 15: ('orientation', 'int'),
    16: ('powerOn', 'bool'), 17: ('disabled', 'bool'),
}
R_BATTERY_STATUS = {
    1: ('health', 'str'), 2: ('level', 'int'), 3: ('plugged', 'bool'), 4: ('present', 'bool'),
    5: ('scale', 'int'), 6: ('isCharging', 'bool'), 7: ('technology', 'str'),
    8: ('temperature', 'int'), 9: ('voltage', 'int'),
}
SCHEMAS = {
    'AuthMessage': {1: ('key', 'bytes'), 2: ('userId', 'str'), 3: ('deviceId', 'str'), 4: ('token', 'str'),
                    5: ('errorCode', AUTH_ERRORS), 6: ('platform', 'str'), 7: ('versionCode', 'int')},
    'ServiceVersionMessage': {1: ('versionCode', 'int'), 2: ('versionName', 'str'), 3: ('forceUpgrade', 'bool'),
                              4: ('modelType', {0: 'UNKNOWN', 1: 'K1'}), 5: ('modelVersion', 'int')},
    'projection.ProjectorStatusMessage': {1: ('status', R_PROJECTOR_STATUS)},
    'remote.BatteryStatusMessage': {1: ('status', R_BATTERY_STATUS)},
    'remote.NameMessage': {1: ('name', 'str')},
    'remote.ConnectedUsersMessage': {1: ('connectedUsersCount', 'int')},
    'remote.VolumeMessage': {1: ('volume', 'int'), 2: ('max', 'int')},
}


def render(schema, payload):
    """Turn a decoded message into a readable dict, using a schema when one is known."""
    out = {}
    for num, values in decode(payload).items():
        name, kind = schema.get(num, (f'#{num}', None)) if schema else (f'#{num}', None)
        value = values[-1]
        if isinstance(kind, dict) and all(isinstance(k, int) for k in kind):
            value = kind.get(value, value) if isinstance(value, int) else render(kind, value)
        elif kind == 'bool':
            value = bool(value)
        elif kind == 'str':
            value = value.decode('utf-8', 'replace')
        elif isinstance(value, (bytes, bytearray)):
            value = value.hex()
        out[name] = value
    return out


# ---------------------------------------------------------------- local identity

class Identity:
    """Our key pair, device id and user id, plus the robot keys seen before (trust on first use)."""

    def __init__(self, path=STATE_FILE):
        self.path = Path(path)
        if self.path.exists():
            state = json.loads(self.path.read_text(encoding='utf-8'))
        else:
            state = {'private_key': base64.b64encode(bytes(PrivateKey.generate())).decode(),
                     'device_id': 'keeckeros-' + uuid.uuid4().hex[:16],
                     'user_id': 'keeckeros-' + uuid.uuid4().hex,
                     'robots': {}}
        self.state = state
        self.private_key = PrivateKey(base64.b64decode(state['private_key']))
        self.public_key = bytes(self.private_key.public_key)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=2), encoding='utf-8')
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass


# ---------------------------------------------------------------- link

class AuthRefused(Exception):
    pass


class RobotLink:
    """One protocol session over a transport exposing send_binary(bytes), recv() and settimeout(s)."""

    def __init__(self, transport, keepalive=True):
        self.transport = transport
        self.box = None
        self.lock = threading.Lock()
        self.closed = threading.Event()
        if keepalive:
            threading.Thread(target=self._keepalive, daemon=True).start()

    @classmethod
    def connect(cls, host, port=DEFAULT_PORT, timeout=10):
        import websocket  # websocket-client
        ws = websocket.create_connection(f'ws://{host}:{port}{WS_PATH}', timeout=timeout)
        return cls(ws)

    def _keepalive(self):
        while not self.closed.wait(KEEPALIVE_S):
            try:
                with self.lock:
                    self.transport.send_binary(PING)
            except Exception:
                return

    def send(self, type_name, payload=b''):
        frame = encode([(2, type_name), (3, payload)])
        if self.box:
            frame = bytes(self.box.encrypt(frame))  # nonce || MAC || ciphertext
        with self.lock:
            self.transport.send_binary(frame)

    def recv(self, timeout):
        """Next protocol message as (type_name, payload); keep-alive echoes are skipped."""
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError
            self.transport.settimeout(remaining)
            try:
                data = self.transport.recv()
            except Exception as exc:
                if type(exc).__name__ in ('WebSocketTimeoutException', 'TimeoutError', 'Empty'):
                    raise TimeoutError from exc
                raise
            if isinstance(data, str):
                data = data.encode()
            if data == PING:
                continue
            if self.box:
                data = self.box.decrypt(data)
            fields = decode(data)
            return fields[2][0].decode(), fields.get(3, [b''])[0]

    def handshake(self, identity, robot_id, accept_new_key=False, timeout=15, log=print):
        self.send('AuthMessage', encode([
            (1, identity.public_key), (2, identity.state['user_id']), (3, identity.state['device_id']),
            (6, PLATFORM), (7, VERSION_CODE)]))
        while True:
            type_name, payload = self.recv(timeout)
            if type_name == 'ServiceVersionMessage':
                log('robot services:', render(SCHEMAS[type_name], payload))
                continue
            if type_name != 'AuthMessage':
                log('ignored before authentication:', type_name)
                continue
            fields = decode(payload)
            if 5 in fields:
                raise AuthRefused(AUTH_ERRORS.get(fields[5][0], fields[5][0]))
            robot_key = bytes(fields[1][0])
            known = identity.state['robots'].get(robot_id)
            robot_key_b64 = base64.b64encode(robot_key).decode()
            if known and known != robot_key_b64 and not accept_new_key:
                raise AuthRefused(f'robot key changed for {robot_id} (use --accept-new-key after a factory reset)')
            identity.state['robots'][robot_id] = robot_key_b64
            identity.save()
            self.box = Box(identity.private_key, PublicKey(robot_key))
            return robot_key

    def close(self):
        self.closed.set()
        try:
            self.transport.close()
        except Exception:
            pass


# ---------------------------------------------------------------- commands

def discover(seconds):
    from zeroconf import ServiceBrowser, Zeroconf
    found = {}

    class Listener:
        def add_service(self, zc, type_, name):
            info = zc.get_service_info(type_, name, 3000)
            if info:
                found[name] = info

        def update_service(self, zc, type_, name):
            self.add_service(zc, type_, name)

        def remove_service(self, zc, type_, name):
            pass

    zc = Zeroconf()
    try:
        ServiceBrowser(zc, SERVICE_TYPE, Listener())
        time.sleep(seconds)
    finally:
        zc.close()
    for name, info in found.items():
        txt = {k.decode(): (v or b'').decode() for k, v in info.properties.items()}
        print(f"{name}\n  addresses: {', '.join(info.parsed_addresses())}  port: {info.port}\n  txt: {txt}")
    if not found:
        print('No _keecker._tcp service found. Same Wi-Fi network? Robot awake?')
    return found


def open_session(args):
    identity = Identity()
    link = RobotLink.connect(args.host, args.port)
    try:
        link.handshake(identity, f'{args.host}:{args.port}', accept_new_key=args.accept_new_key)
    except AuthRefused as exc:
        link.close()
        print(f'Refused by the robot: {exc}')
        if str(exc) == 'UNKNOWN_USER':
            print('Press the top button of the robot 6 times (it says "pairing"), then run the command again.')
        sys.exit(2)
    print('Authenticated, session encrypted.')
    return link


def listen(link, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            type_name, payload = link.recv(deadline - time.monotonic())
        except TimeoutError:
            break
        print(f'<- {type_name}: {render(SCHEMAS.get(type_name), payload)}')


def cmd_status(args):
    link = open_session(args)
    link.send('remote.RegisterMessage', encode([(1, 'com.keecker.common.messages.remote.BatteryStatusMessage')]))
    link.send('projection.ProjectorStatusMessage')
    listen(link, args.seconds)
    link.close()


def cmd_projector(args):
    link = open_session(args)
    if args.led is not None:
        link.send('projection.LedsMessage', encode([(1, args.led == 'on')]))
        print(f'-> projector LED {args.led}')
    if args.tilt is not None:
        if not 0 <= args.tilt <= 90:
            sys.exit('tilt must be between 0 (wall) and 90 (ceiling)')
        link.send('projection.OrientationMessage', encode([(1, args.tilt)]))
        print(f'-> projector tilt {args.tilt}')
    time.sleep(1)
    link.send('projection.ProjectorStatusMessage')
    listen(link, 3)
    link.close()


def cmd_listen(args):
    link = open_session(args)
    listen(link, args.seconds)
    link.close()


def cmd_selftest(_args):
    """Offline check: protobuf round trip and a full handshake against a simulated robot."""
    import queue
    import tempfile

    msg = encode([(1, b'\x01\x02'), (2, 'user'), (5, 3), (7, 20003), (9, True), (10, -1)])
    fields = decode(msg)
    assert fields[1] == [b'\x01\x02'] and fields[2] == [b'user'] and fields[5] == [3]
    assert fields[7] == [20003] and fields[9] == [1] and fields[10] == [-1]

    class Pipe:
        def __init__(self, inbox, outbox):
            self.inbox, self.outbox, self.timeout = inbox, outbox, None

        def send_binary(self, data):
            self.outbox.put(bytes(data))

        def settimeout(self, t):
            self.timeout = t

        def recv(self):
            return self.inbox.get(timeout=self.timeout)

        def close(self):
            pass

    to_robot, to_client = queue.Queue(), queue.Queue()
    robot_key = PrivateKey.generate()

    def robot():
        frame = decode(to_robot.get(timeout=5))
        assert frame[2][0] == b'AuthMessage'
        auth = decode(frame[3][0])
        client_key = PublicKey(bytes(auth[1][0]))
        assert auth[3][0].startswith(b'keeckeros-') and auth[2][0]
        to_client.put(encode([(2, 'ServiceVersionMessage'), (3, encode([(1, 11406), (2, '1.14.6'), (3, False), (4, 1), (5, 0)]))]))
        to_client.put(encode([(2, 'AuthMessage'), (3, encode([(1, bytes(robot_key.public_key))]))]))
        box = Box(robot_key, client_key)
        while True:
            data = to_robot.get(timeout=5)
            if data == PING:
                continue
            assert len(data) >= 24 + 16
            request = decode(box.decrypt(data))
            assert request[2][0] == b'projection.ProjectorStatusMessage'
            status = encode([(1, encode([(1, True), (15, 45), (8, 1)]))])
            to_client.put(bytes(box.encrypt(encode([(2, 'projection.ProjectorStatusMessage'), (3, status)]))))
            return

    worker = threading.Thread(target=robot, daemon=True)
    worker.start()
    with tempfile.TemporaryDirectory() as tmp:
        identity = Identity(Path(tmp) / 'state.json')
        link = RobotLink(Pipe(to_client, to_robot), keepalive=False)
        link.handshake(identity, 'simulated', log=lambda *a: None)
        link.send('projection.ProjectorStatusMessage')
        type_name, payload = link.recv(5)
        status = render(SCHEMAS[type_name], payload)['status']
        assert status == {'ledOn': True, 'orientation': 45, 'displayPosition': 'FRONT_CEILING'}, status
        assert 'simulated' in json.loads((Path(tmp) / 'state.json').read_text())['robots']
    worker.join(5)
    print('selftest OK: protobuf encoding, handshake, encrypted request and reply')


def main():
    parser = argparse.ArgumentParser(description='Open test client for the Keecker K1 companion-app protocol.')
    sub = parser.add_subparsers(dest='command', required=True)

    def robot_args(p):
        p.add_argument('--host', required=True, help='robot IP address (see the discover command)')
        p.add_argument('--port', type=int, default=DEFAULT_PORT)
        p.add_argument('--accept-new-key', action='store_true', help='accept a changed robot key (after a factory reset)')

    p = sub.add_parser('discover', help='find robots on the local network (mDNS)')
    p.add_argument('--seconds', type=float, default=5)
    p.set_defaults(func=lambda a: discover(a.seconds))

    p = sub.add_parser('status', help='pair if needed, then print projector and battery status')
    robot_args(p)
    p.add_argument('--seconds', type=float, default=5)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser('projector', help='switch the projector LED, or tilt the projector (0 wall, 90 ceiling)')
    robot_args(p)
    p.add_argument('--led', choices=['on', 'off'])
    p.add_argument('--tilt', type=int)
    p.set_defaults(func=cmd_projector)

    p = sub.add_parser('listen', help='print every message the robot sends')
    robot_args(p)
    p.add_argument('--seconds', type=float, default=30)
    p.set_defaults(func=cmd_listen)

    p = sub.add_parser('selftest', help='offline check against a simulated robot')
    p.set_defaults(func=cmd_selftest)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
