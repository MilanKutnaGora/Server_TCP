import asyncio
import datetime
import random
import time

# Адрес и порт сервера
SERVER_HOST = "localhost"
SERVER_PORT = 8000

# Путь к файлу лога клиента
CLIENT_LOG_FILE = "client1_log.txt"

# Интервал отправки запросов (в миллисекундах)
REQUEST_INTERVAL_MIN = 300
REQUEST_INTERVAL_MAX = 3000

class Client:
    def __init__(self):
        self.request_count = 0
        self.response_count = 0

    async def run(self):
        reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)

        while True:
            try:
                self.request_count += 1
                request_text = f"[{self.request_count}] PING"
                self.log_request_response(request_text, "")
                writer.write(f"{request_text}\n".encode())
                await writer.drain()

                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
                    if not data:
                        break
                    response = data.decode().strip()
                    self.response_count += 1
                    self.log_request_response(request_text, response)
                except asyncio.TimeoutError:
                    self.log_request_response(request_text, "(таймаут)")

                await asyncio.sleep(random.uniform(REQUEST_INTERVAL_MIN / 1000, REQUEST_INTERVAL_MAX / 1000))
            except Exception as e:
                print(f"Error in client: {e}")
                break

        writer.close()
        await writer.wait_closed()

    def log_request_response(self, request, response):
        now = datetime.datetime.now()
        request_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        if not request:
            response_time = ""
        else:
            response_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        with open(CLIENT_LOG_FILE, "a") as f:
            f.write(f"{request_time};{request};{response_time};{response}\n")

if __name__ == "__main_client_1__":
    client = Client()
    asyncio.run(client.run())