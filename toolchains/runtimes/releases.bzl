"""Release metadata for WASI runtime binaries."""

WASMTIME_RELEASES = {
    "49.0.3": {
        "aarch64-linux": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.3/wasmtime-v49.0.3-aarch64-linux.tar.xz"
            ),
            "shasum": "880fcb026da88ad7fc1713d572b0d03d139758b7da96cd3cb8c9cbf847a521df",
            "prefix": "wasmtime-v49.0.3-aarch64-linux",
            "binary": "wasmtime",
        },
        "aarch64-macos": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.3/wasmtime-v49.0.3-aarch64-macos.tar.xz"
            ),
            "shasum": "d7708ba1cc2da171db2c8273d8602f3e0684935dc7cab40148cdcca1da83c0f8",
            "prefix": "wasmtime-v49.0.3-aarch64-macos",
            "binary": "wasmtime",
        },
        "aarch64-windows": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.3/wasmtime-v49.0.3-aarch64-windows.zip"
            ),
            "shasum": "bb1ece3bf1660db13f4a10f87436a79542af29b3acd75c0ff54bd0ffbc8d5b62",
            "prefix": "wasmtime-v49.0.3-aarch64-windows",
            "binary": "wasmtime",
        },
        "x86_64-linux": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.3/wasmtime-v49.0.3-x86_64-linux.tar.xz"
            ),
            "shasum": "4001225413f208345b980525f31c4080e1873808b38d0ddc7918497340667fbb",
            "prefix": "wasmtime-v49.0.3-x86_64-linux",
            "binary": "wasmtime",
        },
        "x86_64-macos": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.3/wasmtime-v49.0.3-x86_64-macos.tar.xz"
            ),
            "shasum": "bc131e20ed9cb34083fca1a203b38ec9d9e611e96596a10ab0cc9223cb06cd88",
            "prefix": "wasmtime-v49.0.3-x86_64-macos",
            "binary": "wasmtime",
        },
        "x86_64-windows": {
            "url": (
                "https://github.com/bytecodealliance/wasmtime/releases/" +
                "download/v49.0.3/wasmtime-v49.0.3-x86_64-windows.zip"
            ),
            "shasum": "bee8f02158458a5f360412b232543d4fea379b71b94380b806e7980050596c18",
            "prefix": "wasmtime-v49.0.3-x86_64-windows",
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

JBANG_RELEASES = {
    "0.142.0": {
        "default": {
            "url": "https://github.com/jbangdev/jbang/releases/download/v0.142.0/jbang-0.142.0.tar",
            "shasum": "43aaeb9bc30d9331ed57952a872b80dab3dafe8e927f0f7a90a3c8e67d08eaac",
            "prefix": "jbang-0.142.0",
            "binary": "bin/jbang",
        },
    },
}

JDK_RELEASES = {
    "21.0.13+9": {
        "aarch64-linux": {
            "url": (
                "https://github.com/adoptium/temurin21-binaries/releases/download/" +
                "jdk-21.0.13%2B9/OpenJDK21U-jdk_aarch64_linux_hotspot_21.0.13_9.tar.gz"
            ),
            "shasum": "e3522e707fc7dbe2a72c30746b1e7068301a0213ecd213d4491f35a14eb55578",
            "prefix": "jdk-21.0.13+9",
            "binary": "bin/java",
        },
        "x86_64-linux": {
            "url": (
                "https://github.com/adoptium/temurin21-binaries/releases/download/" +
                "jdk-21.0.13%2B9/OpenJDK21U-jdk_x64_linux_hotspot_21.0.13_9.tar.gz"
            ),
            "shasum": "d7f5d5cf865a2902b70ff549b97586a7d3f234e016f041ab447ea740c7d66d1c",
            "prefix": "jdk-21.0.13+9",
            "binary": "bin/java",
        },
    },
}
