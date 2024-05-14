import asyncio
import datetime
import random
import time


# Сервер
async def handle_client(reader, writer, response_num=None):
    client_id = len(server_clients) + 1
    server_clients.append(writer)

    while True:
        try:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode().strip()
            if message:
                request_num, _ = message.split()
                request_num = int(request_num[1:-1])

                # Логирование запроса
                log_request(client_id, request_num, message)

                # Обработка запроса
                if random.random() < 0.1:
                    log_response(client_id, request_num, "(проигнорировано)")
                else:
                    await asyncio.sleep(random.uniform(0.1, 1))
                    response = f"[{response_num}/{request_num}] PONG ({client_id})"
                    writer.write(response.encode() + b"\n")
                    await writer.drain()
                    log_response(client_id, request_num, response)
                    response_num += 1
        except asyncio.exceptions.IncompleteReadError:
            break

    server_clients.remove(writer)
    writer.close()
    await writer.wait_closed()


async def server():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()


# Клиент
async def client(client_id):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    request_num = 0
    while True:
        await asyncio.sleep(random.uniform(0.3, 3))
        request = f"[{request_num}] PING"
        writer.write(request.encode() + b"\n")
        await writer.drain()
        log_client_request(client_id, request_num, request)

        try:
            data = await asyncio.wait_for(reader.read(1024), timeout=1)
            response = data.decode().strip()
            log_client_response(client_id, request_num, response)
        except asyncio.exceptions.TimeoutError:
            log_client_response(client_id, request_num, "(таймаут)")
            continue

        request_num += 1


async def keepalive(response_num=None):
    while True:
        await asyncio.sleep(5)
        for writer in server_clients:
            response = f"[{response_num}] keepalive"
            writer.write(response.encode() + b"\n")
            await writer.drain()
            log_response(0, response_num, response)
            response_num += 1


# Логирование
def log_request(client_id, request_num, message):
    now = datetime.datetime.now()
    with open("server_log.txt", "a") as f:
        f.write(f"{now.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{message};")


def log_response(client_id, request_num, message):
    now = datetime.datetime.now()
    with open("server_log.txt", "a") as f:
        f.write(f"{now.strftime('%H:%M:%S.%f')[:-3]};{message}\n")


def log_client_request(client_id, request_num, message):
    now = datetime.datetime.now()
    with open(f"client{client_id}_log.txt", "a") as f:
        f.write(f"{now.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{message};")


def log_client_response(client_id, request_num, message):
    now = datetime.datetime.now()
    with open(f"client{client_id}_log.txt", "a") as f:
        f.write(f"{now.strftime('%H:%M:%S.%f')[:-3]};{message}\n")


# Точка входа
if __name__ == "__main__":
    server_clients = []
    response_num = 0

    loop = asyncio.get_event_loop()
    loop.create_task(server())
    loop.create_task(client(1))
    loop.create_task(client(2))
    loop.create_task(keepalive())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()