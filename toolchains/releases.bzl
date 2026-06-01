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
