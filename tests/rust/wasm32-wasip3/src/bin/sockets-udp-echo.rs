use test_wasm32_wasip3::sockets::{
    export,
    exports::wasi::cli::run::Guest,
    wasi::sockets::types::{IpAddressFamily, IpSocketAddress, UdpSocket},
};

struct Component;
export!(Component);

async fn echo(family: IpAddressFamily) {
    let sock = UdpSocket::create(family).unwrap();
    let addr = IpSocketAddress::localhost(family, 0);
    sock.bind(addr).unwrap();
    println!("{}", sock.get_local_address().unwrap());
    let (buf, addr) = sock.receive().await.unwrap();

    sock.send(buf, Some(addr)).await.unwrap();
}

impl Guest for Component {
    async fn run() -> Result<(), ()> {
        echo(IpAddressFamily::Ipv4).await;
        Ok(())
    }
}

fn main() {
    unreachable!();
}
