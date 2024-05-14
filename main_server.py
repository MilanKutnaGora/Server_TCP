import asyncio
import datetime
import random
import time

# Порт, на котором будет работать сервер
SERVER_PORT = 8000

# Путь к файлу лога сервера
SERVER_LOG_FILE = "server_log.txt"

# Вероятность игнорирования запроса сервером
IGNORE_PROBABILITY = 0.1

# Интервал отправки сообщений keepalive (в секундах)
KEEPALIVE_INTERVAL = 5

class Server:
    def __init__(self):
        self.request_count = 0
        self.response_count = 0
        self.clients = []

    async def handle_client(self, reader, writer):
        client_id = len(self.clients) + 1
        self.clients.append((reader, writer))
        print(f"New client connected: {client_id}")

        while True:
            try:
                data = await reader.read(1024)
                if not data:
                    break

                request = data.decode().strip()
                if request:
                    self.handle_request(client_id, request)
            except asyncio.exceptions.IncompleteReadError:
                break
            except Exception as e:
                print(f"Error handling client {client_id}: {e}")
                break

        writer.close()
        await writer.wait_closed()
        self.clients.remove((reader, writer))
        print(f"Client {client_id} disconnected")

    def handle_request(self, client_id, request):
        self.request_count += 1
        request_parts = request.split()
        request_num = int(request_parts[0][1:-1])
        request_text = request_parts[1]

        if request_text == "PING":
            if random.random() < IGNORE_PROBABILITY:
                self.log_request_response(request, "(проигнорировано)")
            else:
                response_delay = random.uniform(0.1,1,0)
                asyncio.sleep(response_delay)
                self.response_count += 1
                response_text = f"[{self.response_count}] {self.response_count}/{request_num} PONG ({client_id})"
                self.log_request_response(request, response_text)
                for reader, writer in self.clients:
                    writer.write(f"{response_text}\n".encode())
                    writer.drain()
        else:
            print(f"Received unknown request: {request}")

    def log_request_response(self, request, response):
        now = datetime.datetime.now()
        request_time = now.strftime("%Y-%m-%d;%H:%M:%S.%f")
        if response == "(проигнорировано)":
            response_time = response
        else:
            response_time = now.strftime("%Y-%m-%d;%H:%M:%S.%f")
        with open(SERVER_LOG_FILE, "a") as f:
            f.write(f"{request_time};{request};{response_time};{response}\n")

    async def run(self):
        server = await asyncio.start_server(self.handle_client, "localhost", SERVER_PORT)
        print(f"Server started, listening on port {SERVER_PORT}")

        async def send_keepalive():
            while True:
                await asyncio.sleep(KEEPALIVE_INTERVAL)
                self.response_count += 1
                keepalive_text = f"[{self.response_count}] keepalive"
                self.log_request_response("", keepalive_text)
                for reader, writer in self.clients:
                    writer.write(f"{keepalive_text}\n".encode())
                    await writer.drain()

        asyncio.create_task(send_keepalive())

        async with server:
            await server.serve_forever()

if __name__ == "__main_server__":
    server = Server()
    asyncio.run(server.run())