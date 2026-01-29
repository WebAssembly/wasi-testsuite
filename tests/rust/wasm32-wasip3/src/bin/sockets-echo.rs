use futures::join;
use test_wasm32_wasip3::sockets::{
    export,
    exports::wasi::cli::run::Guest,
    wasi::sockets::types::{IpAddressFamily, IpSocketAddress, Ipv4SocketAddress, TcpSocket},
    wit_stream,
};
use wit_bindgen::StreamResult;

async fn echo(family: IpAddressFamily, addr: IpSocketAddress) {
    let listener = TcpSocket::create(family).unwrap();
    listener.bind(addr).unwrap();
    let addr = listener.get_local_address().unwrap();
    println!("{}", addr);

    let mut accept = listener.listen().unwrap();
    let sock = accept.next().await.unwrap();
    let (mut recv_stream, recv_fut) = sock.receive();

    // Read incoming data.
    // TODO(saul): Not incoming data fits in 100, this must be configurable.
    let (result, data) = recv_stream.read(Vec::with_capacity(100)).await;
    assert_eq!(result, StreamResult::Complete(data.len()));

    // Explicitly drop the stream, since we're not expecting more
    // incoming data.
    drop(recv_stream);
    recv_fut.await.unwrap();

    // Send the response
    let (mut send_tx, send_rx) = wit_stream::new();
    join!(
        async {
            sock.send(send_rx).await.unwrap();
        },
        async {
            let remaining = send_tx.write_all(data).await;
            assert!(remaining.is_empty());
            // Drop the stream, since we don't pretend to send more
            // data.
            drop(send_tx);
        }
    );
}

struct Component;
export!(Component);

impl Guest for Component {
    async fn run() -> Result<(), ()> {
        echo(
            IpAddressFamily::Ipv4,
            IpSocketAddress::Ipv4(Ipv4SocketAddress {
                // TODO(saul): make the port configurable, ideally letting the OS assign it.
                port: 3000,
                address: (127, 0, 0, 1),
            }),
        )
        .await;

        Ok(())
    }
}

fn main() {
    unreachable!()
}
