"""Release metadata for WASI runtime binaries."""

WASMTIME_RELEASES = {
    "49.0.1": {
        "aarch64-linux": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.1/wasmtime-v49.0.1-aarch64-linux.tar.xz"
            ),
            "shasum": "7607529c40fed69c0f5d2a6fafa8c560b9e3c18ded31d8f1b13098afe49b7480",
            "prefix": "wasmtime-v49.0.1-aarch64-linux",
            "binary": "wasmtime",
        },
        "aarch64-macos": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.1/wasmtime-v49.0.1-aarch64-macos.tar.xz"
            ),
            "shasum": "93dde14d4efb20046e5af75517ac6a7f2246f6c2370fecff8f68839d4a9028f7",
            "prefix": "wasmtime-v49.0.1-aarch64-macos",
            "binary": "wasmtime",
        },
        "aarch64-windows": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.1/wasmtime-v49.0.1-aarch64-windows.zip"
            ),
            "shasum": "98c4b6efc086198df195564573904ef0b0bcd435ab15a5469094c953b4b981bc",
            "prefix": "wasmtime-v49.0.1-aarch64-windows",
            "binary": "wasmtime",
        },
        "x86_64-linux": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.1/wasmtime-v49.0.1-x86_64-linux.tar.xz"
            ),
            "shasum": "c71f7e0d30a92e418f0d17db7c6d8f6664c1ad764340a1278678f4209deab534",
            "prefix": "wasmtime-v49.0.1-x86_64-linux",
            "binary": "wasmtime",
        },
        "x86_64-macos": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.1/wasmtime-v49.0.1-x86_64-macos.tar.xz"
            ),
            "shasum": "56355136c4eaba17ef50b0e35e9774e25950333ba007c2a29c45d0906600e827",
            "prefix": "wasmtime-v49.0.1-x86_64-macos",
            "binary": "wasmtime",
        },
        "x86_64-windows": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.1/wasmtime-v49.0.1-x86_64-windows.zip"
            ),
            "shasum": "db0dd3dd77696fa189b08e256a50ddbe46d10a4d1e6c862d8d268ad0abc8c2c1",
            "prefix": "wasmtime-v49.0.1-x86_64-windows",
            "binary": "wasmtime",
        },
    },
}

WAMR_RELEASES = {
    "2.4.5": {
        "x86_64-linux": {
            "url": "https://github.com/wasm-micro-runtime/wasm-micro-runtime/releases/download/WAMR-2.4.5/iwasm-2.4.5-x86_64-ubuntu-22.04.tar.gz",
            "shasum": "61e9d4c77e8f7b06d5cea657b2c319b9be5d51ec51ad8f6f576af84cecd391a3",
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
    "0.17.1": {
        "aarch64-linux": {
            "url": "https://github.com/WasmEdge/WasmEdge/releases/download/0.17.1/WasmEdge-0.17.1-manylinux_2_28_aarch64.tar.gz",
            "shasum": "6d7762429083e787ccbddf629868bb59de4325ccdcc31d9f7bd240adcdd9fe9d",
            "binary": "bin/wasmedge",
        },
        "aarch64-macos": {
            "url": "https://github.com/WasmEdge/WasmEdge/releases/download/0.17.1/WasmEdge-0.17.1-darwin_arm64.tar.gz",
            "shasum": "7f6810f0676f8405586a3edb350ce9a6eb256ef7118f2e327f131b7833d0033e",
            "binary": "bin/wasmedge",
        },
        "x86_64-linux": {
            "url": "https://github.com/WasmEdge/WasmEdge/releases/download/0.17.1/WasmEdge-0.17.1-manylinux_2_28_x86_64.tar.gz",
            "shasum": "27a1abec072ddf45b40e2e81e33c1e5fe9b241f31fd1bbf0182f05097489a07a",
            "binary": "bin/wasmedge",
        },
        "x86_64-macos": {
            "url": "https://github.com/WasmEdge/WasmEdge/releases/download/0.17.1/WasmEdge-0.17.1-darwin_x86_64.tar.gz",
            "shasum": "e96d10da0dfe560ff17775cf4a205ed43cd855dafbb4056ea908865066666660",
            "binary": "bin/wasmedge",
        },
        "x86_64-windows": {
            "url": "https://github.com/WasmEdge/WasmEdge/releases/download/0.17.1/WasmEdge-0.17.1-windows.zip",
            "shasum": "299a73d8b8a4de90ed6f9ace6832bb06eb8d852e02db2b34360a4199905e895f",
            "binary": "bin/wasmedge",
        },
    },
}
