wit_bindgen::generate!({
    inline: r"
	package wasi-testsuite:test;

	world test {
	    include wasi:sockets/imports@0.3.0-rc-2026-01-06;
	}
    ",
    features:["clocks-timezone"],
    pub_export_macro: true,
    default_bindings_module: "test_wasm32_wasip3::sockets",
    additional_derives: [PartialEq, Eq],
    generate_all
});

use wasi::sockets::types::{
    IpAddress, IpAddressFamily, IpSocketAddress, Ipv4SocketAddress, Ipv6SocketAddress,
};

impl IpSocketAddress {
    pub fn ipv4_localhost(port: u16) -> IpSocketAddress {
        IpSocketAddress::Ipv4(Ipv4SocketAddress {
            port,
            address: (127, 0, 0, 1),
        })
    }

    pub fn ipv6_localhost(port: u16) -> IpSocketAddress {
        IpSocketAddress::Ipv6(Ipv6SocketAddress {
            port,
            address: (0, 0, 0, 0, 0, 0, 0, 1),
            flow_info: 0,
            scope_id: 0,
        })
    }

    pub fn ipv4_mapped_ipv6_localhost(port: u16) -> IpSocketAddress {
        IpSocketAddress::Ipv6(Ipv6SocketAddress {
            port,
            address: (0, 0, 0, 0, 0, 0xFFFF, 0x7F00, 0x0001),
            flow_info: 0,
            scope_id: 0,
        })
    }

    pub fn localhost(family: IpAddressFamily, port: u16) -> IpSocketAddress {
        match family {
            IpAddressFamily::Ipv4 => Self::ipv4_localhost(port),
            IpAddressFamily::Ipv6 => Self::ipv6_localhost(port),
        }
    }

    pub fn unspecified(family: IpAddressFamily, port: u16) -> IpSocketAddress {
        match family {
            IpAddressFamily::Ipv4 => Self::new(IpAddress::Ipv4((0, 0, 0, 0)), port),
            IpAddressFamily::Ipv6 => Self::new(IpAddress::Ipv6((0, 0, 0, 0, 0, 0, 0, 0)), port),
        }
    }

    pub fn new(addr: IpAddress, port: u16) -> IpSocketAddress {
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

    pub fn ip_addr(&self) -> IpAddress {
        match self {
            IpSocketAddress::Ipv6(addr) => IpAddress::Ipv6(addr.address),
            IpSocketAddress::Ipv4(addr) => IpAddress::Ipv4(addr.address),
        }
    }

    pub fn port(&self) -> u16 {
        match self {
            IpSocketAddress::Ipv6(addr) => addr.port,
            IpSocketAddress::Ipv4(addr) => addr.port,
        }
    }
}
