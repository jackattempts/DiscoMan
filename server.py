from threading import Thread, Lock
import socket
import random
import json
from hawk_cmds import DISCOVERY_CMDS


class DiscoveryManager(Thread):
    def __init__(self, addr):
        super().__init__()

        self.BUF_SIZE = 1024
        self.addr = addr
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(self.addr)
        self.is_running = True

        self.manager_port = self.__allocate_manager_port()
        self.api_port = self.__allocate_api_port()
        self.client_updater_port = self.__allocate_client_updater_port()
        print(f"DiscoveryManager bound to {self.addr}")
        self.start()

    def get_free_port(self, rmin, rmax):
        port = random.randint(rmin, rmax)
        while self.is_port_in_use(port):
            port = random.randint(rmin, rmax)
        return port

    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("", port)) == 0

    def __allocate_manager_port(self):
        return self.get_free_port(2000, 2500)

    def __allocate_api_port(self):
        return self.get_free_port(3001, 3999)

    def __allocate_client_updater_port(self):
        return self.get_free_port(9000, 10000)

    def __del__(self):
        print("sayonara")

    def run(self):
        while self.is_running:
            try:
                print("Waiting for new discovery")
                data, worker_addr = self.s.recvfrom(1024)
                print(f"DiscoveryManager found a wandering explorer: {worker_addr} with data: {data}")

                if data == DISCOVERY_CMDS.CMD_MANAGER:
                    info = {
                        DISCOVERY_CMDS.MANAGER_PORT: self.manager_port
                    }
                    json_data = json.dumps(info, default=str) + "\n\n"
                    json_data = json_data.encode('utf-8')
                    self.s.sendto(json_data, worker_addr)

                if data == DISCOVERY_CMDS.CMD_API:
                    info = {
                        DISCOVERY_CMDS.API_PORT: self.api_port,
                        DISCOVERY_CMDS.CLIENT_UPDATER_PORT: self.client_updater_port
                    }
                    json_data = json.dumps(info, default=str) + "\n\n"
                    json_data = json_data.encode('utf-8')
                    self.s.sendto(json_data, worker_addr)

            except OSError as e:
                import traceback
                print(traceback.format_exc())
                print(e)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                print(e)

    def shutdown(self):
        print(f"Shutting down HawkManager")
        self.is_running = False
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()


