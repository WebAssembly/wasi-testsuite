wit_bindgen::generate!({
    inline: r"
	package wasi-testsuite:test;

	world test {
	    include wasi:sockets/imports@0.3.0-rc-2026-01-06;
	    include wasi:cli/command@0.3.0-rc-2026-01-06;
	}
    ",
    features:["clocks-timezone"],
    additional_derives: [PartialEq, Eq],
    generate_all
});

use wasi::sockets::types::{
    ErrorCode, IpAddress, IpAddressFamily, IpSocketAddress, Ipv4SocketAddress, Ipv6SocketAddress,
    TcpSocket,
};

struct Component;

export!(Component);

const IPV6_LOCALHOST: IpAddress = IpAddress::Ipv6((0, 0, 0, 0, 0, 0, 0, 1));
const IPV4_LOCALHOST: IpAddress = IpAddress::Ipv4((127, 0, 0, 1));
const IPV4_MAPPED_LOCALHOST: IpAddress = IpAddress::Ipv6((0, 0, 0, 0, 0, 0xFFFF, 0x7F00, 0x0001));

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

    fn ip_addr(&self) -> IpAddress {
        match self {
            IpSocketAddress::Ipv6(addr) => IpAddress::Ipv6(addr.address),
            IpSocketAddress::Ipv4(addr) => IpAddress::Ipv4(addr.address),
        }
    }

    fn port(&self) -> u16 {
        match self {
            IpSocketAddress::Ipv6(addr) => addr.port,
            IpSocketAddress::Ipv4(addr) => addr.port,
        }
    }
}

fn test_invalid_address_family(family: IpAddressFamily) {
    let sock = TcpSocket::create(family).unwrap();

    let addr = match family {
        IpAddressFamily::Ipv4 => IpSocketAddress::new(IPV6_LOCALHOST, 0),
        IpAddressFamily::Ipv6 => IpSocketAddress::new(IPV4_LOCALHOST, 0),
    };

    let result = sock.bind(addr);
    assert!(matches!(result, Err(ErrorCode::InvalidArgument)));
}

fn test_ephemeral_port_assignment(family: IpAddressFamily) {
    let sock = TcpSocket::create(family).unwrap();

    let addr = match family {
        IpAddressFamily::Ipv4 => IpSocketAddress::new(IPV4_LOCALHOST, 0),
        IpAddressFamily::Ipv6 => IpSocketAddress::new(IPV6_LOCALHOST, 0),
    };

    sock.bind(addr).unwrap();
    let bound = sock.get_local_address().unwrap();

    assert_eq!(addr.ip_addr(), bound.ip_addr());
    // Randomly assigned port.
    assert_ne!(addr.port(), bound.port());
}

fn test_non_unicast(family: IpAddressFamily) {
    let mut non_unicast_addresses = Vec::new();

    match family {
        IpAddressFamily::Ipv4 => {
            // Multicast
            for nibble in 224..=239 {
                non_unicast_addresses.push(IpAddress::Ipv4((nibble, 0, 0, 1)));
            }
            // Limited broadcast
            non_unicast_addresses.push(IpAddress::Ipv4((255, 255, 255, 255)));
        }
        IpAddressFamily::Ipv6 => {
            // Multicast
            for b in 0xff00..=0xffff {
                non_unicast_addresses.push(IpAddress::Ipv6((b, 0, 0, 0, 0, 0, 0, 1)));
            }
        }
    };

    for addr in non_unicast_addresses {
        let sock = TcpSocket::create(family).unwrap();
        let socket_addr = IpSocketAddress::new(addr, 0);
        let result = sock.bind(socket_addr);

        assert!(matches!(result, Err(ErrorCode::InvalidArgument)));
    }
}

fn test_dual_stack_support() {
    let sock = TcpSocket::create(IpAddressFamily::Ipv6).unwrap();
    let addr = IpSocketAddress::new(IPV4_MAPPED_LOCALHOST, 0);
    let result = sock.bind(addr);

    assert!(matches!(result, Err(ErrorCode::InvalidArgument)));
}

impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        test_invalid_address_family(IpAddressFamily::Ipv4);
        test_invalid_address_family(IpAddressFamily::Ipv6);
        test_ephemeral_port_assignment(IpAddressFamily::Ipv4);
        test_ephemeral_port_assignment(IpAddressFamily::Ipv6);
        test_non_unicast(IpAddressFamily::Ipv4);
        test_non_unicast(IpAddressFamily::Ipv6);
        test_dual_stack_support();
        Ok(())
    }
}

fn main() {
    unreachable!()
}
