import ldmud
import socket, struct

class Interactive:
    def __init__(self, control_ob, hostname, hostaddr, hostport, mudport):
        self.control_ob = control_ob
        self.hostname = hostname
        self.hostaddr = hostaddr
        self.hostport = hostport
        self.mudport = mudport

        self.inputto = []
        self.options = {}
        self.last_cmd = ldmud.efuns.time()
        self.snooper = None

    def is_control_ob(self, check_ob):
        if isinstance(self.control_ob, str):
            return check_ob.name == self.control_ob
        else:
            return check_ob == self.control_ob

    def call_control_ob(self, fun, *args):
        return ldmud.efuns.call_other(self.control_ob, fun, *args)

    def get_sockaddr(self):
        info = socket.getaddrinfo(self.hostaddr, self.hostport, type=socket.SOCK_STREAM)
        if not len(info):
            return None

        info = info[0]

        raw = struct.pack("<H", info[0]) + struct.pack(">H", info[4][1])

        if info[0] == socket.AF_INET6:
            raw += 4*b"\x00"
        raw += socket.inet_pton(info[0], info[4][0])
        if info[0] == socket.AF_INET:
            raw +=  8*b"\x00"
        elif info[0] == socket.AF_INET6:
            raw +=  4*b"\x00"

        return ldmud.Array(raw)

    def update_idle(self):
        self.last_cmd = ldmud.efuns.time()

    def get_idle(self):
        return ldmud.efuns.time() - self.last_cmd
