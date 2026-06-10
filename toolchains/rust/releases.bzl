"""Pinned Rust release metadata for the hermetic toolchain.

Hashes are the official sha256 sums published in
``https://static.rust-lang.org/dist/channel-rust-<version>.toml``. Bumping the
toolchain means updating ``RUST_VERSION`` together with every hash below.
"""

RUST_VERSION = "1.96.0"

_BASE_URL = "https://static.rust-lang.org/dist"

# Combined ``rust`` package per host triple. Contains rustc, cargo, rustdoc,
# clippy, rustfmt and the host standard library.
RUST_HOST_RELEASES = {
    "aarch64-apple-darwin": "f04a974f3579d3524f6b9bc6490a27c9fb358050e7cd8a641945f30bf24c1dce",
    "aarch64-pc-windows-msvc": "a62ef64a3ae41ce3a5bba1a27d3d183cfadcd5bb4ab3b6e0093144f96185009a",
    "aarch64-unknown-linux-gnu": "371eadcca97062219cbd8593628eb5d2802bc370515d085fedce1b56b2baed57",
    "x86_64-apple-darwin": "63a6d717a5e5392ac43f0a1593e7aabe6128c8685d318cb890603b1688cb3339",
    "x86_64-pc-windows-msvc": "ff7672090c1f5bcc102a1702bb33cd3cb64d671a6897e195b1b72c974664b90b",
    "x86_64-unknown-linux-gnu": "c295047583a56238ea06b43f849f4b877fa12bfd4c7103f8d9a74c94c9c4e108",
}

# Per-target ``rust-std`` package. Host independent; one archive per wasm target.
RUST_STD_RELEASES = {
    "wasm32-wasip1": "7750b9ed4ad9fa32662f983e9730dcdc97a461fad1d9e9305fa7173f39848e83",
    "wasm32-wasip2": "17a511eade6b74a86a31af9f7498d416a717472a91d11b180ac760944e69599e",
}

def rust_host_url(triple: str) -> str:
    return "{}/rust-{}-{}.tar.xz".format(_BASE_URL, RUST_VERSION, triple)

def rust_std_url(target: str) -> str:
    return "{}/rust-std-{}-{}.tar.xz".format(_BASE_URL, RUST_VERSION, target)
