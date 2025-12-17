import subprocess
import socket
from typing import List
from .test_case import Output, Config, Protocol, ProtocolType


def serve(argv: List[str], config: Config) -> Output:
    if config.protocol is None:
        raise RuntimeError("Protocol configuration is required for connection based tests")

    if config.protocol.type == ProtocolType.TCP:
        with subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as server:
            # Something went wrong starting the server.
            if server.poll() is not None:
                _, err = server.communicate()
                return Output(server.returncode, "", err, "")

            # Business as usual.
            # We get to test the connection.
            if server.stdout is None:
                return _kill_server(server)

            ack = server.stdout.readline().strip()
            if ack == "OK":
                return _test_tcp(server, config.protocol)

            # We didn't receive the ack message that we were expecting.
            return _kill_server(server)

    raise RuntimeError(f"Unimplemented support for protocol {config.protocol.type}")


def _test_tcp(server: subprocess.Popen, prot: Protocol) -> Output:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.settimeout(5)
            sock.connect((prot.address, prot.port))
            sock.sendall(prot.request.encode('utf-8'))
            response = sock.recv(len(prot.response))
            server.wait(timeout=5)
            out, err = server.communicate()
            return Output(server.returncode, out, err, response.decode('utf-8'))
        except (socket.timeout, subprocess.TimeoutExpired):
            return _kill_server(server)


def _kill_server(server: subprocess.Popen) -> Output:
    server.kill()
    out, err = server.communicate()
    return Output(server.returncode, out, err, "")
