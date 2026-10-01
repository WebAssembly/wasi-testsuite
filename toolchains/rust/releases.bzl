"""Pinned Rust release metadata for the hermetic toolchain.

Hashes are the official sha256 sums published in
``https://static.rust-lang.org/dist/channel-rust-<version>.toml``. Bumping the
toolchain means updating ``RUST_VERSION`` together with every hash below.
"""

RUST_VERSION = "1.98.1"

_BASE_URL = "https://static.rust-lang.org/dist"

# Combined ``rust`` package per host triple. Contains rustc, cargo, rustdoc,
# clippy, rustfmt and the host standard library.
RUST_HOST_RELEASES = {
    "aarch64-apple-darwin": "8f7c9de34c12c66dc55a6dbdd63b2b9645d4418775d4b975b0078a602f66e3e8",
    "aarch64-pc-windows-msvc": "a9e186a281308cdf876ab6a0e2c37d75ef43e1c466a44641d301120e0f3358c5",
    "aarch64-unknown-linux-gnu": "0b514a8cc1cbcd939bff0f151661fe58b6ea5c7a7f645a5098c69e32e8c1e0a2",
    "x86_64-apple-darwin": "0d5aea6011d3b553e5aa71580b0cd7f9f0614eef17f7e5767e6bc161541ed85f",
    "x86_64-pc-windows-msvc": "c34c3f01633efe5edac0e1ed1ee66d5ec13a7f27e57c149059ed6bdbe0534407",
    "x86_64-unknown-linux-gnu": "5326b36c53de11d148c8f8dab6553a3d1006c2cfd32123683073fad3c302605b",
}

# Per-target ``rust-std`` package. Host independent; one archive per wasm target.
RUST_STD_RELEASES = {
    "wasm32-wasip1": "b5e91be9ed75c632a4c576d3c4c725ab143cd48c27c345133b97ccdf217b23e7",
    "wasm32-wasip2": "efb0d2df60c97ab652d9cccd41b1e21b4c370fe5da6b66ad5f1466bac26c4195",
}

def rust_host_url(triple: str) -> str:
    return "{}/rust-{}-{}.tar.xz".format(_BASE_URL, RUST_VERSION, triple)

def rust_std_url(target: str) -> str:
    return "{}/rust-std-{}-{}.tar.xz".format(_BASE_URL, RUST_VERSION, target)
