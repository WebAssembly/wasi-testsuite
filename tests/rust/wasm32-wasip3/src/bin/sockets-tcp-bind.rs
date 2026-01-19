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

impl IpSocketAddress {
    fn ipv4_localhost(port: u16) -> IpSocketAddress {
        IpSocketAddress::Ipv4(Ipv4SocketAddress {
            port,
            address: (127, 0, 0, 1),
        })
    }

    fn ipv6_localhost(port: u16) -> IpSocketAddress {
        IpSocketAddress::Ipv6(Ipv6SocketAddress {
            port,
            address: (0, 0, 0, 0, 0, 0, 0, 1),
            flow_info: 0,
            scope_id: 0,
        })
    }

    fn ipv6_mapped_localhost(port: u16) -> IpSocketAddress {
        IpSocketAddress::Ipv6(Ipv6SocketAddress {
            port,
            address: (0, 0, 0, 0, 0, 0xFFFF, 0x7F00, 0x0001),
            flow_info: 0,
            scope_id: 0,
        })
    }

    fn localhost(family: IpAddressFamily, port: u16) -> IpSocketAddress {
        match family {
            IpAddressFamily::Ipv4 => Self::ipv4_localhost(port),
            IpAddressFamily::Ipv6 => Self::ipv6_localhost(port),
        }
    }

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
        IpAddressFamily::Ipv4 => IpSocketAddress::localhost(IpAddressFamily::Ipv6, 0),
        IpAddressFamily::Ipv6 => IpSocketAddress::localhost(IpAddressFamily::Ipv4, 0),
    };

    let result = sock.bind(addr);
    assert!(matches!(result, Err(ErrorCode::InvalidArgument)));
}

fn test_ephemeral_port_assignment(family: IpAddressFamily) {
    let sock = TcpSocket::create(family).unwrap();
    let addr = IpSocketAddress::localhost(family, 0);

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
    let addr = IpSocketAddress::ipv6_mapped_localhost(0);
    let result = sock.bind(addr);

    assert!(matches!(result, Err(ErrorCode::InvalidArgument)));
}

fn test_bind_addrinuse(family: IpAddressFamily) {
    let addr = IpSocketAddress::localhost(family, 0);

    let sock1 = TcpSocket::create(family).unwrap();
    sock1.bind(addr).unwrap();
    sock1.listen().unwrap();

    let bound_addr = sock1.get_local_address().unwrap();
    let sock2 = TcpSocket::create(family).unwrap();
    let result = sock2.bind(bound_addr);
    assert_eq!(result, Err(ErrorCode::AddressInUse));
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
        test_bind_addrinuse(IpAddressFamily::Ipv4);
        test_bind_addrinuse(IpAddressFamily::Ipv6);
        Ok(())
    }
}

fn main() {
    unreachable!()
}
