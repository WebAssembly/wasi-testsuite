wit_bindgen::generate!({
    inline: r"
	package wasi-testsuite:test;

	world test {
	    include wasi:sockets/imports@0.3.0-rc-2026-01-06;
	    include wasi:cli/command@0.3.0-rc-2026-01-06;
	}
    ",
    features:["clocks-timezone"],
    generate_all
});

use wasi::sockets::types::{
    ErrorCode, IpAddress, IpAddressFamily, IpSocketAddress, Ipv4SocketAddress, Ipv6SocketAddress,
    TcpSocket,
};

struct Component;

export!(Component);

pub const IPV6_LOCALHOST: (u16, u16, u16, u16, u16, u16, u16, u16) = (0, 0, 0, 0, 0, 0, 0, 1);
pub const IPV4_LOCALHOST: (u8, u8, u8, u8) = (127, 0, 0, 1);

impl IpSocketAddress {
    fn new(addr: IpAddress, port: u16) -> IpSocketAddress {
        match addr {
            IpAddress::Ipv4(addr) => IpSocketAddress::Ipv4(Ipv4SocketAddress {
                port,
                address: addr,
            }),
            IpAddress::Ipv6(addr) => IpSocketAddress::Ipv6(Ipv6SocketAddress {
                port,
                address: addr,
                flow_info: 0,
                scope_id: 0,
            }),
        }
    }
}

fn test_invalid_address_family(family: IpAddressFamily) {
    let sock = TcpSocket::create(family).unwrap();

    let addr = match family {
        IpAddressFamily::Ipv4 => IpSocketAddress::new(IpAddress::Ipv6(IPV6_LOCALHOST), 0),
        IpAddressFamily::Ipv6 => IpSocketAddress::new(IpAddress::Ipv4(IPV4_LOCALHOST), 0),
    };

    let result = sock.bind(addr);
    assert!(matches!(result, Err(ErrorCode::InvalidArgument)));
}

impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        test_invalid_address_family(IpAddressFamily::Ipv4);
        test_invalid_address_family(IpAddressFamily::Ipv6);
        Ok(())
    }
}

fn main() {
    unreachable!()
}
