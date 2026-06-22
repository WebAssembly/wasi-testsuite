"""Release metadata for WASI runtime binaries."""

WASMTIME_RELEASES = {
    "45.0.0": {
        "aarch64-linux": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v45.0.0/wasmtime-v45.0.0-aarch64-linux.tar.xz"
            ),
            "shasum": "4a27083ba8d3c64526b2d469f50e6539cb4c1dd9d08336e0d8953bca616737e3",
            "prefix": "wasmtime-v45.0.0-aarch64-linux",
            "binary": "wasmtime",
        },
        "aarch64-macos": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v45.0.0/wasmtime-v45.0.0-aarch64-macos.tar.xz"
            ),
            "shasum": "8c589a1feb6578ddfd76d4ee07bac551d7f3069d6cef9b2ae5e87e630b5198db",
            "prefix": "wasmtime-v45.0.0-aarch64-macos",
            "binary": "wasmtime",
        },
        "aarch64-windows": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v45.0.0/wasmtime-v45.0.0-aarch64-windows.zip"
            ),
            "shasum": "e080b367ecaba5fd6fb18fa9825af2e6f5c68ce0bc67d1df3941d9472fc31869",
            "prefix": "wasmtime-v45.0.0-aarch64-windows",
            "binary": "wasmtime",
        },
        "x86_64-linux": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v45.0.0/wasmtime-v45.0.0-x86_64-linux.tar.xz"
            ),
            "shasum": "9d92e6dc04630f617e0e5d532327a5a917ac4898587e07f4fb7a5fc7fffef760",
            "prefix": "wasmtime-v45.0.0-x86_64-linux",
            "binary": "wasmtime",
        },
        "x86_64-macos": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v45.0.0/wasmtime-v45.0.0-x86_64-macos.tar.xz"
            ),
            "shasum": "b01b421613d9e067103efb701cd66f436020b32f6e955125fac9eaf34fa5bce7",
            "prefix": "wasmtime-v45.0.0-x86_64-macos",
            "binary": "wasmtime",
        },
        "x86_64-windows": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v45.0.0/wasmtime-v45.0.0-x86_64-windows.zip"
            ),
            "shasum": "edb9572c6e8ae7c51053af826a8bc85bf205a759c9e83ddb08a941b26e297706",
            "prefix": "wasmtime-v45.0.0-x86_64-windows",
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
