class DiscoverTheManager:
    def __init__(self, port):
        self.discovery_port = port
        self.port = random.randint(20000, 30000)
        self.bcast = IP_ADDRESS.B_CAST

    def do(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.2)
        sock.bind(("", self.port))
        sock.sendto(DISCOVERY_CMDS.CMD_MANAGER, (self.bcast, self.discovery_port))

        buffer, manager_addr = sock.recvfrom(1024)

        for data in (json.loads(x.strip()) for x in buffer.splitlines() if len(x.strip()) > 0):
            if DISCOVERY_CMDS.MANAGER_PORT in data:
                print(f"Discovered manager running on {manager_addr[0]} at port {data[DISCOVERY_CMDS.MANAGER_PORT]}")
                return manager_addr[0], data[DISCOVERY_CMDS.MANAGER_PORT]
            else:
                return None
