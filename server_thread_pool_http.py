# server.py
from socket import *
import socket
import sys
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = b""
    try:
        print(f"[DEBUG] Connected from {address}")
        while True:
            data = connection.recv(4096)
            if not data:
                break
            rcv += data
            if b"\r\n\r\n" in rcv:
                break  # End of headers
    except Exception as e:
        print(f"[ERROR] Exception while receiving data from {address}: {e}")
        connection.close()
        return

    try:
        request_text = rcv.decode()
        print(f"[DEBUG] Request from {address}:\n{request_text}")

        hasil = httpserver.proses(request_text)
        hasil = hasil + b"\r\n\r\n"
        connection.sendall(hasil)
        print(f"[DEBUG] Response sent to {address}")
    except Exception as e:
        print(f"[ERROR] Exception while processing request from {address}: {e}")
    finally:
        connection.close()
        print(f"[DEBUG] Connection closed for {address}")
        return

def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8885))
    my_socket.listen(10)
    print("Thread-based server listening on port 8885...")

    with ThreadPoolExecutor(20) as executor:
        while True:
            try:
                connection, client_address = my_socket.accept()
                future = executor.submit(ProcessTheClient, connection, client_address)
                the_clients.append(future)
                active = [x for x in the_clients if not x.done()]
                print(f"Active threads: {len(active)}")
            except KeyboardInterrupt:
                print("Shutting down server...")
                break
            except Exception as e:
                print(f"[ERROR] Server error: {e}")
                continue

def main():
    Server()

if __name__ == "__main__":
    main()
