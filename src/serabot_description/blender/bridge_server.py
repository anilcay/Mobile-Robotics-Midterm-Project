"""Local code-execution bridge for a running Blender instance.

Run inside Blender:  blender --python bridge_server.py
Listens on 127.0.0.1 only. Each connection sends one JSON request
{"code": "..."} and closes its write side; the code runs on Blender's main
thread and the reply is {"ok", "output", "result", "error"}. Code may set a
variable named ``result`` to return a JSON-serialisable value.
"""

import contextlib
import io
import json
import queue
import socket
import threading
import traceback

import bpy

HOST = '127.0.0.1'
PORT = 9877
TIMEOUT_S = 300.0

_jobs: 'queue.Queue[dict]' = queue.Queue()
_namespace: dict = {'bpy': bpy}


def _run_job(job: dict) -> None:
    """Execute one request on the main thread and store the reply."""
    out = io.StringIO()
    reply = {'ok': True, 'output': '', 'result': None, 'error': ''}
    _namespace.pop('result', None)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            exec(compile(job['code'], '<bridge>', 'exec'), _namespace)
        result = _namespace.get('result')
        json.dumps(result)
        reply['result'] = result
    except Exception:
        reply['ok'] = False
        reply['error'] = traceback.format_exc()
    reply['output'] = out.getvalue()
    job['reply'] = reply
    job['done'].set()


def _poll() -> float:
    """Timer callback: drain pending jobs on Blender's main thread."""
    while True:
        try:
            job = _jobs.get_nowait()
        except queue.Empty:
            return 0.1
        _run_job(job)


def _handle(conn: socket.socket) -> None:
    with conn:
        chunks = []
        while True:
            data = conn.recv(65536)
            if not data:
                break
            chunks.append(data)
        try:
            request = json.loads(b''.join(chunks).decode('utf-8'))
            job = {'code': request['code'], 'done': threading.Event()}
        except (ValueError, KeyError) as exc:
            reply = {'ok': False, 'output': '', 'result': None, 'error': repr(exc)}
        else:
            _jobs.put(job)
            if job['done'].wait(TIMEOUT_S):
                reply = job['reply']
            else:
                reply = {'ok': False, 'output': '', 'result': None, 'error': 'timeout'}
        conn.sendall(json.dumps(reply).encode('utf-8'))


def _serve() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print(f'[bridge] listening on {HOST}:{PORT}')
        while True:
            conn, _ = srv.accept()
            threading.Thread(target=_handle, args=(conn,), daemon=True).start()


def start() -> None:
    """Start the listener thread and the main-thread job timer."""
    threading.Thread(target=_serve, daemon=True).start()
    bpy.app.timers.register(_poll, persistent=True)


start()
