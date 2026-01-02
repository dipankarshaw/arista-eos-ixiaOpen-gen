import time
import streamlit as st
import snappi


st.set_page_config(page_title="Traffic & BGP", layout="wide")

page = st.sidebar.radio("Go to", ("Traffic", "BGP"))


def run_snappi_traffic(common: dict, flow1: dict, flow2: dict):
    """Push up to two directional flows based on form input."""
    api = snappi.api(location=common["controller"], verify=common["verify_ssl"])

    config = api.config()
    port_a = config.ports.port(name="port_a", location=flow1["tx_loc"])[-1]
    port_b = config.ports.port(name="port_b", location=flow1["rx_loc"])[-1]

    f1 = config.flows.flow(name="flow1")[-1]
    f1.tx_rx.port.tx_name = port_a.name
    f1.tx_rx.port.rx_name = port_b.name
    f1.size.fixed = flow1["frame_size"]
    f1.duration.fixed_packets.packets = flow1["packet_count"]
    f1.rate.pps = flow1["pps"]
    eth1 = f1.packet.ethernet()[-1]
    eth1.src.value = flow1["mac_src"]
    eth1.dst.value = flow1["mac_dst"]
    ip1 = f1.packet.ipv4()[-1]
    ip1.src.value = flow1["ip_src"]
    ip1.dst.value = flow1["ip_dst"]
    tcp1 = f1.packet.tcp()[-1]
    tcp1.src_port.value = flow1["tcp_sport"]
    tcp1.dst_port.value = flow1["tcp_dport"]
    f1.metrics.enable = True

    if flow2["enable"]:
        f2 = config.flows.flow(name="flow2")[-1]
        f2.tx_rx.port.tx_name = port_b.name
        f2.tx_rx.port.rx_name = port_a.name
        f2.size.fixed = flow2["frame_size"]
        f2.duration.fixed_packets.packets = flow2["packet_count"]
        f2.rate.pps = flow2["pps"]
        eth2 = f2.packet.ethernet()[-1]
        eth2.src.value = flow2["mac_src"]
        eth2.dst.value = flow2["mac_dst"]
        ip2 = f2.packet.ipv4()[-1]
        ip2.src.value = flow2["ip_src"]
        ip2.dst.value = flow2["ip_dst"]
        tcp2 = f2.packet.tcp()[-1]
        tcp2.src_port.value = flow2["tcp_sport"]
        tcp2.dst_port.value = flow2["tcp_dport"]
        f2.metrics.enable = True

    api.set_config(config)

    cs = api.control_state()
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
    api.set_control_state(cs)

    time.sleep(common["wait_time"])

    req = api.metrics_request()
    req.flow.flow_names = [f.name for f in config.flows]
    metrics = api.get_metrics(req)
    return metrics


def run_snappi_bgp(params: dict):
    """Configure a simple BGP peer on ixia-c using snappi and return peer metrics."""
    api = snappi.api(location=params["controller"], verify=params["verify_ssl"])

    cfg = api.config()

    # Port and interface
    port = cfg.ports.port(name="port1", location=params["port_loc"])[-1]
    dev = cfg.devices.device(name=params["device_name"])[-1]
    eth = dev.ethernets.ethernet(name="eth0")[-1]
    eth.connection.port_name = port.name
    eth.mac = params["mac"]
    eth.mtu = params["mtu"]
    ipv4 = eth.ipv4_addresses.ipv4(name="v4")[-1]
    ipv4.address = params["ip"]
    ipv4.gateway = params["gateway"]
    ipv4.prefix = params["prefix"]

    # BGP
    dev.bgp.router_id = params["router_id"]
    iface = dev.bgp.ipv4_interfaces.add()
    iface.ipv4_name = ipv4.name
    peer = iface.peers.add()
    peer.name = "peer1"
    peer.as_type = peer.EBGP
    peer.as_number = params["peer_as"]
    peer.peer_address = params["peer_ip"]
    peer.advanced.keep_alive_interval = params["keepalive"]
    peer.advanced.hold_time_interval = params["hold"]

    # Advertised routes
    v4_routes = peer.v4_routes.add()
    v4_routes.name = "v4_routes"
    addr = v4_routes.addresses.add()
    addr.address = params["route_start"]
    addr.count = params["route_count"]
    addr.step = params["route_step"]
    addr.prefix = params["route_prefix"]

    api.set_config(cfg)

    cs = api.control_state()
    cs.protocol.all.state = cs.protocol.all.START
    api.set_control_state(cs)

    time.sleep(params["wait"])

    req = api.metrics_request()
    req.bgpv4.peer_names = [peer.name]
    metrics = api.get_metrics(req)
    return metrics


if page == "Traffic":
    st.title("Traffic")
    with st.form("traffic_form"):
        controller = st.text_input("Controller URL", "https://clab-ceos-ixia-c:8443")
        verify_ssl = st.checkbox("Verify TLS", value=False)
        enable_f2 = st.checkbox("Enable Reverse Flow (Eth2 → Eth1)", value=True)
        wait_time = st.number_input("Wait Time After Start (seconds)", min_value=1, value=10)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Eth1 → Eth2")
            f1_tx_loc = st.text_input("TX Port (eth1)", "eth1")
            f1_rx_loc = st.text_input("RX Port (eth2)", "eth2")
            f1_mac_src = st.text_input("Src MAC", "00:00:00:00:00:01")
            f1_mac_dst = st.text_input("Dst MAC", "00:00:00:00:00:02")
            f1_ip_src = st.text_input("Src IPv4", "10.1.1.2")
            f1_ip_dst = st.text_input("Dst IPv4", "10.2.2.2")
            f1_tcp_sport = st.number_input("TCP Src Port", min_value=1, max_value=65535, value=5000, key="f1_sport")
            f1_tcp_dport = st.number_input("TCP Dst Port", min_value=1, max_value=65535, value=6000, key="f1_dport")
            f1_frame = st.number_input("Frame Size (bytes)", min_value=64, max_value=9216, value=128, key="f1_frame")
            f1_pkts = st.number_input("Packet Count", min_value=1, value=1000, key="f1_pkts")
            f1_pps = st.number_input("Packets Per Second", min_value=1, value=100, key="f1_pps")

        with col2:
            st.subheader("Eth2 → Eth1")
    
            f2_tx_loc = st.text_input("TX Port (eth2)", "eth2")
            f2_rx_loc = st.text_input("RX Port (eth1)", "eth1")
            f2_mac_src = st.text_input("Src MAC", "00:00:00:00:00:02")
            f2_mac_dst = st.text_input("Dst MAC", "00:00:00:00:00:01")
            f2_ip_src = st.text_input("Src IPv4", "10.2.2.2")
            f2_ip_dst = st.text_input("Dst IPv4", "10.1.1.2")
            f2_tcp_sport = st.number_input("TCP Src Port", min_value=1, max_value=65535, value=6000, key="f2_sport")
            f2_tcp_dport = st.number_input("TCP Dst Port", min_value=1, max_value=65535, value=5000, key="f2_dport")
            f2_frame = st.number_input("Frame Size (bytes)", min_value=64, max_value=9216, value=128, key="f2_frame")
            f2_pkts = st.number_input("Packet Count", min_value=1, value=1000, key="f2_pkts")
            f2_pps = st.number_input("Packets Per Second", min_value=1, value=100, key="f2_pps")

        submitted = st.form_submit_button("Start Traffic")

    if submitted:
        common = {
            "controller": controller,
            "verify_ssl": verify_ssl,
            "wait_time": int(wait_time),
        }
        flow1 = {
            "tx_loc": f1_tx_loc,
            "rx_loc": f1_rx_loc,
            "mac_src": f1_mac_src,
            "mac_dst": f1_mac_dst,
            "ip_src": f1_ip_src,
            "ip_dst": f1_ip_dst,
            "tcp_sport": int(f1_tcp_sport),
            "tcp_dport": int(f1_tcp_dport),
            "frame_size": int(f1_frame),
            "packet_count": int(f1_pkts),
            "pps": int(f1_pps),
        }
        flow2 = {
            "enable": enable_f2,
            "tx_loc": f2_tx_loc,
            "rx_loc": f2_rx_loc,
            "mac_src": f2_mac_src,
            "mac_dst": f2_mac_dst,
            "ip_src": f2_ip_src,
            "ip_dst": f2_ip_dst,
            "tcp_sport": int(f2_tcp_sport),
            "tcp_dport": int(f2_tcp_dport),
            "frame_size": int(f2_frame),
            "packet_count": int(f2_pkts),
            "pps": int(f2_pps),
        }
        try:
            metrics = run_snappi_traffic(common, flow1, flow2)
            st.success("Traffic run complete")
            st.write("Flow Metrics:")
            st.table([
                {
                    "flow": m.name,
                    "tx_frames": m.frames_tx,
                    "rx_frames": m.frames_rx,
                }
                for m in metrics.flow_metrics
            ])
        except Exception as exc:  # noqa: BLE001
            st.error(f"Traffic run failed: {exc}")

elif page == "BGP":
    st.title("BGP")
    with st.form("bgp_form"):
        st.subheader("Controller & Timing")
        controller = st.text_input("Controller URL", "https://clab-ceos-ixia-c:8443")
        verify_ssl = st.checkbox("Verify TLS", value=False)
        wait = st.number_input("Wait After Start (sec)", min_value=1, value=5)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("eth1 Configuration")
            st.markdown("**Port & Interface**")
            eth1_port_loc = st.text_input("Port Location", "eth1", key="eth1_port")
            eth1_device_name = st.text_input("Device Name", "dut-eth1", key="eth1_device")
            eth1_mac = st.text_input("MAC Address", "00:00:00:00:00:01", key="eth1_mac")
            eth1_ip = st.text_input("IPv4 Address", "10.1.1.2", key="eth1_ip")
            eth1_gateway = st.text_input("Gateway", "10.1.1.1", key="eth1_gw")
            eth1_prefix = st.number_input("Prefix Length", min_value=1, max_value=32, value=24, key="eth1_prefix")
            eth1_mtu = st.number_input("MTU", min_value=576, max_value=9200, value=1500, key="eth1_mtu")

            st.markdown("**BGP Peer**")
            eth1_router_id = st.text_input("Router ID", "192.1.1.1", key="eth1_rid")
            eth1_peer_ip = st.text_input("Peer IP", "10.1.1.1", key="eth1_peer_ip")
            eth1_peer_as = st.number_input("Local ASN", min_value=1, max_value=4294967295, value=65001, key="eth1_peer_as")

            st.markdown("**Advertised Routes**")
            eth1_route_start = st.text_input("Route Start", "192.0.2.0", key="eth1_route_start")
            eth1_route_count = st.number_input("Route Count", min_value=1, value=10, key="eth1_route_count")
            eth1_route_prefix = st.number_input("Route Prefix", min_value=1, max_value=32, value=32, key="eth1_route_prefix")
            eth1_route_step = st.number_input("Route Step (uint32)", min_value=1, value=1, key="eth1_route_step")

        with col2:
            st.subheader("eth2 Configuration")
            st.markdown("**Port & Interface**")
            eth2_port_loc = st.text_input("Port Location", "eth2", key="eth2_port")
            eth2_device_name = st.text_input("Device Name", "dut-eth2", key="eth2_device")
            eth2_mac = st.text_input("MAC Address", "00:00:00:00:00:02", key="eth2_mac")
            eth2_ip = st.text_input("IPv4 Address", "10.2.2.2", key="eth2_ip")
            eth2_gateway = st.text_input("Gateway", "10.2.2.1", key="eth2_gw")
            eth2_prefix = st.number_input("Prefix Length", min_value=1, max_value=32, value=24, key="eth2_prefix")
            eth2_mtu = st.number_input("MTU", min_value=576, max_value=9200, value=1500, key="eth2_mtu")

            st.markdown("**BGP Peer**")
            eth2_router_id = st.text_input("Router ID", "192.2.2.2", key="eth2_rid")
            eth2_peer_ip = st.text_input("Peer IP", "10.2.2.1", key="eth2_peer_ip")
            eth2_peer_as = st.number_input("Local ASN", min_value=1, max_value=4294967295, value=65002, key="eth2_peer_as")

            st.markdown("**Advertised Routes**")
            eth2_route_start = st.text_input("Route Start", "192.1.2.0", key="eth2_route_start")
            eth2_route_count = st.number_input("Route Count", min_value=1, value=10, key="eth2_route_count")
            eth2_route_prefix = st.number_input("Route Prefix", min_value=1, max_value=32, value=32, key="eth2_route_prefix")
            eth2_route_step = st.number_input("Route Step (uint32)", min_value=1, value=1, key="eth2_route_step")

        submitted_bgp = st.form_submit_button("Push BGP Config")

    if submitted_bgp:
        keepalive = 30
        hold = 90
        
        eth1_params = {
            "controller": controller,
            "verify_ssl": verify_ssl,
            "wait": int(wait),
            "port_loc": eth1_port_loc,
            "device_name": eth1_device_name,
            "mac": eth1_mac,
            "ip": eth1_ip,
            "gateway": eth1_gateway,
            "prefix": int(eth1_prefix),
            "mtu": int(eth1_mtu),
            "router_id": eth1_router_id,
            "peer_ip": eth1_peer_ip,
            "peer_as": int(eth1_peer_as),
            "keepalive": keepalive,
            "hold": hold,
            "route_start": eth1_route_start,
            "route_count": int(eth1_route_count),
            "route_prefix": int(eth1_route_prefix),
            "route_step": int(eth1_route_step),
        }
        
        eth2_params = {
            "controller": controller,
            "verify_ssl": verify_ssl,
            "wait": int(wait),
            "port_loc": eth2_port_loc,
            "device_name": eth2_device_name,
            "mac": eth2_mac,
            "ip": eth2_ip,
            "gateway": eth2_gateway,
            "prefix": int(eth2_prefix),
            "mtu": int(eth2_mtu),
            "router_id": eth2_router_id,
            "peer_ip": eth2_peer_ip,
            "peer_as": int(eth2_peer_as),
            "keepalive": keepalive,
            "hold": hold,
            "route_start": eth2_route_start,
            "route_count": int(eth2_route_count),
            "route_prefix": int(eth2_route_prefix),
            "route_step": int(eth2_route_step),
        }
        
        try:
            # Configure both eth1 and eth2 BGP
            api = snappi.api(location=controller, verify=verify_ssl)
            cfg = api.config()
            
            # eth1 configuration
            port1 = cfg.ports.port(name="port1", location=eth1_params["port_loc"])[-1]
            dev1 = cfg.devices.device(name=eth1_params["device_name"])[-1]
            eth1 = dev1.ethernets.ethernet(name="eth1_0")[-1]
            eth1.connection.port_name = port1.name
            eth1.mac = eth1_params["mac"]
            eth1.mtu = eth1_params["mtu"]
            ipv4_1 = eth1.ipv4_addresses.ipv4(name="v4_1")[-1]
            ipv4_1.address = eth1_params["ip"]
            ipv4_1.gateway = eth1_params["gateway"]
            ipv4_1.prefix = eth1_params["prefix"]
            
            dev1.bgp.router_id = eth1_params["router_id"]
            iface1 = dev1.bgp.ipv4_interfaces.add()
            iface1.ipv4_name = ipv4_1.name
            peer1 = iface1.peers.add()
            peer1.name = "peer_eth1"
            peer1.as_type = peer1.EBGP
            peer1.as_number = eth1_params["peer_as"]
            peer1.peer_address = eth1_params["peer_ip"]
            peer1.advanced.keep_alive_interval = eth1_params["keepalive"]
            peer1.advanced.hold_time_interval = eth1_params["hold"]
            
            v4_routes1 = peer1.v4_routes.add()
            v4_routes1.name = "v4_routes_eth1"
            addr1 = v4_routes1.addresses.add()
            addr1.address = eth1_params["route_start"]
            addr1.count = eth1_params["route_count"]
            addr1.step = eth1_params["route_step"]
            addr1.prefix = eth1_params["route_prefix"]
            
            # eth2 configuration
            port2 = cfg.ports.port(name="port2", location=eth2_params["port_loc"])[-1]
            dev2 = cfg.devices.device(name=eth2_params["device_name"])[-1]
            eth2 = dev2.ethernets.ethernet(name="eth2_0")[-1]
            eth2.connection.port_name = port2.name
            eth2.mac = eth2_params["mac"]
            eth2.mtu = eth2_params["mtu"]
            ipv4_2 = eth2.ipv4_addresses.ipv4(name="v4_2")[-1]
            ipv4_2.address = eth2_params["ip"]
            ipv4_2.gateway = eth2_params["gateway"]
            ipv4_2.prefix = eth2_params["prefix"]
            
            dev2.bgp.router_id = eth2_params["router_id"]
            iface2 = dev2.bgp.ipv4_interfaces.add()
            iface2.ipv4_name = ipv4_2.name
            peer2 = iface2.peers.add()
            peer2.name = "peer_eth2"
            peer2.as_type = peer2.EBGP
            peer2.as_number = eth2_params["peer_as"]
            peer2.peer_address = eth2_params["peer_ip"]
            peer2.advanced.keep_alive_interval = eth2_params["keepalive"]
            peer2.advanced.hold_time_interval = eth2_params["hold"]
            
            v4_routes2 = peer2.v4_routes.add()
            v4_routes2.name = "v4_routes_eth2"
            addr2 = v4_routes2.addresses.add()
            addr2.address = eth2_params["route_start"]
            addr2.count = eth2_params["route_count"]
            addr2.step = eth2_params["route_step"]
            addr2.prefix = eth2_params["route_prefix"]
            
            api.set_config(cfg)
            
            cs = api.control_state()
            cs.protocol.all.state = cs.protocol.all.START
            api.set_control_state(cs)
            
            time.sleep(int(wait))
            
            req = api.metrics_request()
            req.bgpv4.peer_names = [peer1.name, peer2.name]
            metrics = api.get_metrics(req)
            
            st.success("BGP config pushed and protocols started for both eth1 and eth2")
            st.write("Peer Metrics:")
            st.table([
                {
                    "peer": m.name,
                    "state": m.session_state,
                    "fsm_state": m.fsm_state,
                    "tx_routes": m.routes_advertised,
                    "rx_routes": m.routes_received,
                }
                for m in metrics.bgpv4_metrics
            ])
        except Exception as exc:  # noqa: BLE001
            st.error(f"BGP push failed: {exc}")

    st.divider()
    st.subheader("Stop BGP Session")
    with st.form("bgp_stop_form"):
        stop_controller = st.text_input("Controller URL", "https://clab-ceos-ixia-c:8443", key="stop_controller")
        stop_verify_ssl = st.checkbox("Verify TLS", value=False, key="stop_verify")
        
        submitted_stop = st.form_submit_button("Stop BGP Session")

    if submitted_stop:
        try:
            api = snappi.api(location=stop_controller, verify=stop_verify_ssl)
            cs = api.control_state()
            cs.protocol.all.state = cs.protocol.all.STOP
            api.set_control_state(cs)
            st.success("BGP session stopped successfully")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Failed to stop BGP session: {exc}")
