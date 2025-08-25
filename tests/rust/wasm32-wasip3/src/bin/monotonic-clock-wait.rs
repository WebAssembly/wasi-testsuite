extern crate wit_bindgen;

wit_bindgen::generate!({
    inline: r"
  package test:test;

  world test {
      include wasi:clocks/imports@0.3.0-rc-2025-08-15;
      include wasi:cli/command@0.3.0-rc-2025-08-15;
  }
",
    // Work around https://github.com/bytecodealliance/wasm-tools/issues/2285.
    features:["clocks-timezone"],
    async: [
        "wasi:cli/run@0.3.0-rc-2025-08-15#run",
    ],
    generate_all
});

use wasi::clocks::monotonic_clock;

struct Component;
export!(Component);

impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        {
            let start = monotonic_clock::now();
            let how_long = 1_000_000u64;
            monotonic_clock::wait_for(how_long).await;
            let end = monotonic_clock::now();
            assert!(end.wrapping_sub(start) >= how_long);
        }

        {
            let start = monotonic_clock::now();
            let how_long = 1_000_000u64;
            let when = start + how_long;
            monotonic_clock::wait_until(when).await;
            let end = monotonic_clock::now();
            assert!(end.wrapping_sub(start) >= how_long);
        }

        Ok(())
    }
}

fn main() { unreachable!("main is a stub"); }
