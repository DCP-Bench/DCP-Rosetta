"""Reach a licence server from a container with no network (see evaluation.licences).

The evaluator mounts a Unix socket forwarded to the server and sets DCP_LICENCE_RELAY
and DCP_LICENCE_PORT; the licence client file it mounts names 127.0.0.1 as the server.
A runner for a `server` licence calls `start()` before the solver loads its licence:

    import licence_relay
    licence_relay.start()

Without those variables (no licence, or a size-limited run) it does nothing. An
integration copies this file into its image beside runtime.py.
"""
import os
import socket
import threading


def _pump(source, sink):
    try:
        while chunk := source.recv(65536):
            sink.sendall(chunk)
    except OSError:
        pass
    finally:
        for end in (source, sink):
            try:
                end.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def _serve(client, path):
    upstream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        upstream.connect(path)
    except OSError:
        client.close()
        return
    for source, sink in ((client, upstream), (upstream, client)):
        threading.Thread(target=_pump, args=(source, sink), daemon=True).start()


def start():
    """Listen on 127.0.0.1:DCP_LICENCE_PORT and forward to the relay socket; True if started."""
    path, port = os.environ.get("DCP_LICENCE_RELAY"), os.environ.get("DCP_LICENCE_PORT")
    if not path or not port:
        return False
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", int(port)))
    listener.listen(16)

    def accept():
        while True:
            client, _ = listener.accept()
            threading.Thread(target=_serve, args=(client, path), daemon=True).start()

    threading.Thread(target=accept, daemon=True).start()
    return True
