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

use core::future::Future;
use core::pin::pin;
use core::task::{Context, Poll, Waker};
use wasi::clocks::monotonic_clock;

struct Component;
export!(Component);
impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        sleep_10ms().await;
        sleep_0ms();
        sleep_backwards_in_time();
        Ok(())
    }
}

async fn sleep_10ms() {
    let dur = 10_000_000;
    monotonic_clock::wait_until(monotonic_clock::now() + dur).await;
    monotonic_clock::wait_for(dur).await;
}

fn sleep_0ms() {
    let mut cx = Context::from_waker(Waker::noop());

    assert_eq!(
        pin!(monotonic_clock::wait_until(monotonic_clock::now())).poll(&mut cx),
        Poll::Ready(()),
        "waiting until now() is ready immediately",
    );
    assert_eq!(
        pin!(monotonic_clock::wait_for(0)).poll(&mut cx),
        Poll::Ready(()),
        "waiting for 0 is ready immediately",
    );
}

fn sleep_backwards_in_time() {
    let mut cx = Context::from_waker(Waker::noop());

    assert_eq!(
        pin!(monotonic_clock::wait_until(monotonic_clock::now() - 1)).poll(&mut cx),
        Poll::Ready(()),
        "waiting until instant which has passed is ready immediately",
    );
}

fn main() {}

