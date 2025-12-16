from .test_case import Output, Config, Protocol, ProtocolResponse, ProtocolType
from typing import List

import subprocess
import time
import socket

def serve(argv: List[str], config: Config) -> Output:
    if config.protocol.type == ProtocolType.TCP:
        with subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as server:
            # TODO(saul):
            # * We might want to use a different heuristic, since this
            #   is likely error prone and could cause flakiness
            # * At the very least inspect stdout for confirmation that the server started.
            # * Port availability could become tricky. Perhaps we could derive an available port
            #   from the client/server on the fly rather than hard coding it.
            time.sleep(2)
            return _test_tcp(server, config.protocol)

    raise RuntimeError(f"Unimplemented support for protocol {config.protocol.type}")

def _test_tcp(server: subprocess.Popen, prot: Protocol) -> Output:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        sock.connect((prot.address, prot.port))
        sock.sendall(prot.request.encode('utf-8'))
        response = sock.recv(len(prot.response))

    # TODO(saul): Check for the exit status code. It's possible that
    # we might get a legit non-zero exit code e.g., permission related
    # or port not available
    return Output(0, "", "", ProtocolResponse(response))
