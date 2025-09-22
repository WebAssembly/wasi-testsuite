extern crate wit_bindgen;

wit_bindgen::generate!({
    inline: r"
  package test:test;

  world test {
      include wasi:clocks/imports@0.3.0-rc-2025-09-16;
      include wasi:cli/command@0.3.0-rc-2025-09-16;
  }
",
    // Work around https://github.com/bytecodealliance/wasm-tools/issues/2285.
    features:["clocks-timezone"],
    generate_all
});

use core::task::{Context, Poll, Waker};
use monotonic_clock::Instant;
use std::future::Future;
use wasi::clocks::monotonic_clock;

// Offsets relative to "now" at which to wait_until(), in nanoseconds.
// These are 20 values chosen uniformly randomly over the range [-5
// milliseconds, +10 milliseconds].
const OFFSETS: &[i64] = &[
    6628081, 851815, 6208892, 1511472, -1206606, 8926559, 2828840, 4561077, 5375188, 8253693,
    2403137, 6055827, 5658461, -3972826, -561642, 6360445, 9966678, 2946734, 2012267, -3456550,
];

fn add_offset(t: Instant, dt: i64) -> Instant {
    if dt < 0 {
        t.saturating_sub(-dt as u64)
    } else {
        t.saturating_add(dt as u64)
    }
}

async fn test_multi_clock_wait() {
    let mut cx = Context::from_waker(Waker::noop());

    let times: Vec<Instant> = {
        let start = monotonic_clock::now();
        OFFSETS.iter().map(|ns| add_offset(start, *ns)).collect()
    };

    let mut completed: Vec<bool> = times.iter().map(|_| false).collect();
    let mut waitables: Vec<_> = times
        .iter()
        .map(|t| -> _ { Box::pin(monotonic_clock::wait_until(*t)) })
        .collect();

    for i in 0..waitables.len() {
        if !completed[i] {
            waitables[i].as_mut().await;
            assert!(times[i] <= monotonic_clock::now());
            completed[i] = true;
        }

        for j in (i + 1)..waitables.len() {
            if !completed[j] && times[j] <= times[i] {
                assert_eq!(
                    waitables[j].as_mut().poll(&mut cx),
                    Poll::Ready(()),
                    "waitable that should fire in past is ready"
                );
                completed[j] = true;
            }
        }
    }
}

struct Component;
export!(Component);
impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        test_multi_clock_wait().await;
        Ok(())
    }
}

fn main() {
    unreachable!("main is a stub");
}
