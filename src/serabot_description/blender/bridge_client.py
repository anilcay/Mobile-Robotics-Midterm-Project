"""Send Python code to a Blender instance running bridge_server.py.

Usage:
  python bridge_client.py script.py      # run a file
  python bridge_client.py -c "print(1)"  # run inline code
Exit code is 1 if the code raised inside Blender.
"""

import argparse
import json
import os
import socket
import sys

HOST = '127.0.0.1'
PORT = 9877


def send(code: str, timeout: float = 310.0) -> dict:
    """Run ``code`` in Blender and return the bridge reply."""
    with socket.create_connection((HOST, PORT), timeout=timeout) as conn:
        conn.sendall(json.dumps({'code': code}).encode('utf-8'))
        conn.shutdown(socket.SHUT_WR)
        chunks = []
        while True:
            data = conn.recv(65536)
            if not data:
                break
            chunks.append(data)
    return json.loads(b''.join(chunks).decode('utf-8'))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('script', nargs='?', help='Python file to run in Blender')
    group.add_argument('-c', dest='code', help='inline Python code')
    args = parser.parse_args()
    if args.code is not None:
        code = args.code
    else:
        path = os.path.abspath(args.script)
        with open(path, encoding='utf-8') as f:
            # Scripts locate repo files relative to their own path.
            code = f'__file__ = {path!r}\n' + f.read()
    reply = send(code)
    sys.stdout.write(reply['output'])
    if reply['result'] is not None:
        print(json.dumps(reply['result'], indent=2, ensure_ascii=False))
    if not reply['ok']:
        sys.stderr.write(reply['error'])
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
