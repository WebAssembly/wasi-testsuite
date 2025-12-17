wit_bindgen::generate!({
    inline: r"
	package wasi-testsuite:test;

	world test {
	    include wasi:sockets/imports@0.3.0-rc-2025-09-16;
	    include wasi:cli/command@0.3.0-rc-2025-09-16;
	}
    ",
    features:["clocks-timezone"],
    generate_all
});

use std::fmt;
use wasi::sockets::types::{
    ErrorCode, IpAddressFamily, IpSocketAddress, Ipv4SocketAddress, Ipv6SocketAddress, TcpSocket,
};

use futures::try_join;
use wit_bindgen::StreamResult;

impl std::fmt::Display for IpSocketAddress {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            IpSocketAddress::Ipv4(Ipv4SocketAddress { port, address }) => {
                write!(
                    f,
                    "{}.{}.{}.{}:{}",
                    address.0, address.1, address.2, address.3, port
                )
            }
            IpSocketAddress::Ipv6(Ipv6SocketAddress { port, address, .. }) => {
                write!(
                    f,
                    "{}.{}.{}.{}.{}.{}.{}.{}:{}",
                    address.0,
                    address.1,
                    address.2,
                    address.3,
                    address.4,
                    address.5,
                    address.6,
                    address.7,
                    port
                )
            }
        }
    }
}

async fn echo(family: IpAddressFamily, addr: IpSocketAddress) -> Result<(), ErrorCode> {
    let listener = TcpSocket::create(family)?;
    listener.bind(addr)?;
    println!("OK");

    let mut accept = listener.listen()?;
    if let Some(sock) = accept.next().await {
        let (mut recv_stream, recv_fut) = sock.receive();

        // Read incoming data.
        let (result, data) = recv_stream.read(Vec::with_capacity(100)).await;
        assert_eq!(result, StreamResult::Complete(data.len()));

        // Explicitly drop the stream, since we're not expecting more
        // incoming data.
        drop(recv_stream);
        recv_fut.await?;

        // Send the response
        let (mut send_tx, send_rx) = wit_stream::new();
        try_join!(
            async {
                sock.send(send_rx).await?;
                Ok::<(), ErrorCode>(())
            },
            async {
                let remaining = send_tx.write_all(data).await;
                assert!(remaining.is_empty());
                // Drop the stream, since we don't pretend to send more
                // data.
                drop(send_tx);
                Ok::<(), ErrorCode>(())
            }
        )?;
    }

    Ok(())
}

struct Component;
export!(Component);

impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        let echo_result = echo(
            IpAddressFamily::Ipv4,
            IpSocketAddress::Ipv4(Ipv4SocketAddress {
                port: 3000,
                address: (127, 0, 0, 1),
            }),
        )
        .await;

        match echo_result {
            Err(_) => std::process::abort(),
            _ => Ok(()),
        }
    }
}

fn main() {
    unreachable!()
}
