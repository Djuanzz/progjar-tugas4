from socket import *
import socket
import time
import sys
import os
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

def ProcessTheClient(connection_data):
    connection, address = connection_data
    httpserver = HttpServer()
    buffer = b""

    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            buffer += data
            if b"\r\n\r\n" in buffer:
                break  # end of HTTP headers
    except Exception as e:
        print(f"[ERROR] Exception while receiving data: {e}")
        connection.close()
        return

    try:
        request_text = buffer.decode()
        print(f"[DEBUG] Request from {address}:\n{request_text}")

        response = httpserver.proses(request_text)
        connection.sendall(response + b"\r\n\r\n")
        print(f"[DEBUG] Response sent to {address}")

    except Exception as e:
        print(f"[ERROR] Exception while processing request: {e}")
    finally:
        connection.close()
        print(f"[DEBUG] Connection closed for {address}")

def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind(('0.0.0.0', 8889))
    my_socket.listen(10)

    print("Process-based server listening on port 8889...")

    with ProcessPoolExecutor(max_workers=10) as executor:
        while True:
            try:
                connection, client_address = my_socket.accept()
                future = executor.submit(ProcessTheClient, (connection, client_address))
                the_clients.append(future)

                active = [x for x in the_clients if not x.done()]
                print(f"Active processes: {len(active)}")

            except KeyboardInterrupt:
                print("Shutting down server...")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue

def main():
    Server()

if __name__ == "__main__":
    main()
