"""
Серверное приложение для соединений
"""
import asyncio
from asyncio import transports


class ClientProtocol(asyncio.Protocol):
    login: str
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server
        self.login = None

    def data_received(self, data: bytes):
        decoded = data.decode()
        print(decoded)

        if self.login is None:
            # login:User
            if decoded.startswith("login:"):
                login_try = decoded.replace("login:", "").replace("\r\n", "")

                if (self.server.logins.count(login_try)==0):
                    self.login = login_try
                    self.server.logins.append(login_try)
                    self.transport.write(
                        f"Привет, {self.login}!/n/r last 10 messages {self.server.last_10_msgs}".encode()
                    )

                else:
                    self.transport.write(
                        f"Привет, try another login!".encode()
                    )
        else:
                self.send_message(decoded)

    def send_message(self, message):
        format_string = f"<{self.login}> {message}"
        encoded = format_string.encode()

        for client in self.server.clients:
            temp_last_10_messages=self.server.last_10_msgs
            self.server.last_10_msgs.append(encoded)
            while len(self.server.last_10_msgs)>10:
                self.server.last_10_msgs.pop(0)
            if client.login != self.login:
                client.transport.write(encoded)

    def connection_made(self, transport: transports.Transport):
        self.transport = transport
        self.server.clients.append(self)
        print("Соединение установлено")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("Соединение разорвано")


class Server:
    clients: list
    logins: list
    last_10_msgs: list
    def __init__(self):
        self.clients = []
        self.logins = []
        self.last_10_msgs=[]

    def create_protocol(self):
        return ClientProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.create_protocol,
            "127.0.0.1",
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")