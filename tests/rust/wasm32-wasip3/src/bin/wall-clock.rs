extern crate wit_bindgen;

wit_bindgen::generate!({
    inline: r"
  package test:test;

  world test {
      include wasi:clocks/imports@0.3.0-rc-2025-08-15;
  }
",
    // Work around https://github.com/bytecodealliance/wasm-tools/issues/2285.
    features:["clocks-timezone"],
    generate_all
});

use wasi::clocks::wall_clock;

const NANOSECOND: u32 = 1;
const MICROSECOND: u32 = NANOSECOND * 1_000;
const MILLISECOND: u32 = MICROSECOND * 1_000;
const SECOND: u32 = MILLISECOND * 1_000;

fn verify_datetime(t: wall_clock::Datetime) {
    assert!(t.nanoseconds < SECOND)
}

fn main() {
    // Not much we can assert about wall-clock time.
    verify_datetime(wall_clock::now());
    verify_datetime(wall_clock::get_resolution());
}
