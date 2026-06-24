"""Release metadata for WASI runtime binaries."""

WASMTIME_RELEASES = {
   "46.0.1": {
        "aarch64-linux": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v46.0.1/wasmtime-v46.0.1-aarch64-linux.tar.xz"
            ),
            "shasum": "071c4def2a08f0ebc95c52dfd4f2886eb697ba495804217cf76e13b09d70a1be",
            "prefix": "wasmtime-v46.0.1-aarch64-linux",
            "binary": "wasmtime",
        },
        "aarch64-macos": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v46.0.1/wasmtime-v46.0.1-aarch64-macos.tar.xz"
            ),
            "shasum": "acee50be70dbe90b0ab2ac7db1321fc44715153a1b1cc58291c97b6d7cffc558",
            "prefix": "wasmtime-v46.0.1-aarch64-macos",
            "binary": "wasmtime",
        },
        "aarch64-windows": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v46.0.1/wasmtime-v46.0.1-aarch64-windows.zip"
            ),
            "shasum": "65631cfcb5a5f34d10a6ff87dda52cb17722847cb9ffed00633bf8313a3231ee",
            "prefix": "wasmtime-v46.0.1-aarch64-windows",
            "binary": "wasmtime",
        },
        "x86_64-linux": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v46.0.1/wasmtime-v46.0.1-x86_64-linux.tar.xz"
            ),
            "shasum": "9ae0b17ea298bcc52277a8208d6ab7fae8e1a89579672f9d82f9d86c116edb62",
            "prefix": "wasmtime-v46.0.1-x86_64-linux",
            "binary": "wasmtime",
        },
        "x86_64-macos": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v46.0.1/wasmtime-v46.0.1-x86_64-macos.tar.xz"
            ),
            "shasum": "0513db67e7089c7e5f743a01427782bc4def83854222f4bc9b1d75f0b925240b",
            "prefix": "wasmtime-v46.0.1-x86_64-macos",
            "binary": "wasmtime",
        },
        "x86_64-windows": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v46.0.1/wasmtime-v46.0.1-x86_64-windows.zip"
            ),
            "shasum": "99f038066b16cb3aaf63c1d282a9d7ba7befafbadf7aa8827cc4c712d96bc31a",
            "prefix": "wasmtime-v46.0.1-x86_64-windows",
            "binary": "wasmtime",
        },
    },
}

WAMR_RELEASES = {
    "2.4.4": {
        "x86_64-linux": {
            "url": "https://github.com/bytecodealliance/wasm-micro-runtime/releases/download/WAMR-2.4.4/iwasm-2.4.4-x86_64-ubuntu-22.04.tar.gz",
            "shasum": "ec60ff8daed26319dfc4371843c56ac2dfadd20e2218cbbca97aecb8b390b7a8",
            "binary": "iwasm",
        },
    },
}

WAZERO_RELEASES = {
    "1.12.0": {
        "aarch64-linux": {
            "url": "https://github.com/wazero/wazero/releases/download/v1.12.0/wazero_1.12.0_linux_arm64.tar.gz",
            "shasum": "b5e5105a8bc4817a117e52402713f0628ebe13ecec5c4e63d541c430ca9bf259",
            "binary": "wazero",
        },
        "aarch64-macos": {
            "url": "https://github.com/wazero/wazero/releases/download/v1.12.0/wazero_1.12.0_darwin_arm64.tar.gz",
            "shasum": "c9e811bb8638163a294de8579923a4ce759846dc04f964468855a23e69bbe73c",
            "binary": "wazero",
        },
        "x86_64-linux": {
            "url": "https://github.com/wazero/wazero/releases/download/v1.12.0/wazero_1.12.0_linux_amd64.tar.gz",
            "shasum": "88019896950340e8839b94af0510b248c3400d8d8f4a9b335dcaad93ac0484ff",
            "binary": "wazero",
        },
        "x86_64-macos": {
            "url": "https://github.com/wazero/wazero/releases/download/v1.12.0/wazero_1.12.0_darwin_amd64.tar.gz",
            "shasum": "4a142b30ab0c7cfeae3fb453c5d2f3beca5af823d5aeeb4c0de458f89e9d5bb8",
            "binary": "wazero",
        },
        "x86_64-windows": {
            "url": "https://github.com/wazero/wazero/releases/download/v1.12.0/wazero_1.12.0_windows_amd64.zip",
            "shasum": "32342e7e6ffc6d1016ae35e9e15479ef718076f27afdad1e89bb1bb6796efeee",
            "binary": "wazero",
        },
    },
}

WASMEDGE_RELEASES = {
    "0.17.0": {
        "aarch64-linux": {
            "url": "https://github.com/WasmEdge/WasmEdge/releases/download/0.17.0/WasmEdge-0.17.0-manylinux_2_28_aarch64.tar.gz",
            "shasum": "6d3aa5a43fd0998b11812e99b46e90a282f3caaacc9cfef14b67f3438b63e804",
            "binary": "bin/wasmedge",
        },
        "aarch64-macos": {
            "url": "https://github.com/WasmEdge/WasmEdge/releases/download/0.17.0/WasmEdge-0.17.0-darwin_arm64.tar.gz",
            "shasum": "ae97ff792ac1bf7bcf703b20926b9bac168e5b6260930d13a156dc19e68a67c5",
            "binary": "bin/wasmedge",
        },
        "x86_64-linux": {
            "url": "https://github.com/WasmEdge/WasmEdge/releases/download/0.17.0/WasmEdge-0.17.0-manylinux_2_28_x86_64.tar.gz",
            "shasum": "5d8165559c553eacc9b87db1799c2204e056db8609bedbf61eb29f8a21a42993",
            "binary": "bin/wasmedge",
        },
        "x86_64-macos": {
            "url": "https://github.com/WasmEdge/WasmEdge/releases/download/0.17.0/WasmEdge-0.17.0-darwin_x86_64.tar.gz",
            "shasum": "5742f7d19bbdb983f4df57114b085f908bae06f705ea3e167f802a66bd9e0342",
            "binary": "bin/wasmedge",
        },
        "x86_64-windows": {
            "url": "https://github.com/WasmEdge/WasmEdge/releases/download/0.17.0/WasmEdge-0.17.0-windows.zip",
            "shasum": "9d38f0f8a8211c9f4a355e7c7e825e4545f3a12908de7f4eec2aa8e84fb593a6",
            "binary": "bin/wasmedge",
        },
    },
}
