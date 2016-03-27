class SocketIOError(Exception):
    pass


class ConnectionError(SocketIOError):
    pass


class TimeoutError(SocketIOError):
    pass


class PacketError(SocketIOError):
    pass
