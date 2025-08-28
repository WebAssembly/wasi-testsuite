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

use monotonic_clock::{Duration, Instant};
use wasi::clocks::monotonic_clock;

const NANOSECOND: Duration = 1;
const MICROSECOND: Duration = NANOSECOND * 1_000;
const MILLISECOND: Duration = MICROSECOND * 1_000;
const SECOND: Duration = MILLISECOND * 1_000;
const MINUTE: Duration = SECOND * 60;
const HOUR: Duration = MINUTE * 60;
const DAY: Duration = HOUR * 24;

fn compute_duration(start: Instant, end: Instant) -> Duration {
    // Assume that this test takes less than a day to run (in terms of
    // the monotonic clock), and that therefore the difference between
    // any two `monotonic-clock#now` calls should be less than a day;
    // otherwise it's probably a clock that erroneously went backwards
    // or jumped too far forwards or something.
    const MAX_TEST_DURATION: Duration = DAY;

    assert!(start <= end);
    let dur = end - start;
    assert!(dur < MAX_TEST_DURATION);
    dur
}

async fn test_wait_for() {
    let start = monotonic_clock::now();
    monotonic_clock::wait_for(1 * MILLISECOND).await;
    let end = monotonic_clock::now();
    assert!(compute_duration(start, end) >= 1 * MILLISECOND);

    monotonic_clock::wait_for(0).await;
}

async fn test_wait_until() {
    monotonic_clock::wait_until(monotonic_clock::now()).await;
    monotonic_clock::wait_until(0).await;

    let start = monotonic_clock::now();
    monotonic_clock::wait_until(start + 1 * MILLISECOND).await;
    let end = monotonic_clock::now();
    assert!(compute_duration(start, end) >= 1 * MILLISECOND);
}

fn test_resolution() {
    assert!(monotonic_clock::get_resolution() > 0);
}

struct Component;
export!(Component);
impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        test_wait_for().await;
        test_wait_until().await;
        test_resolution();
        Ok(())
    }
}

fn main() {
    unreachable!("main is a stub");
}
