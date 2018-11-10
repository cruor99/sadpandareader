from socketIO_client import SocketIO


url = "http://1dvxtg49adq5f5jtzm2a04p2sr2pje3fem1x6gfu2cyhr30p.pushould.com"
client_token = "6rgcw2zlr4ubpvcegjajqpnmehx5gp5zm1yigjzp1mgfvy6c"


def do_notify(response):
    print(response["message"])

socketio = SocketIO(url, params={"transports": ["polling", "websocket"]})
socketio.on('send', do_notify)
socketio.emit("subscribe", {"room": "sadpandapush",
                            "token": client_token})
socketio.wait()
