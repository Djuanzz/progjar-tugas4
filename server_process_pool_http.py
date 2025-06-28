from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = ""
    print(f"[DEBUG] Connected from {address}")
    while True:
        try:
            data = connection.recv(1024)
            if data:
                d = data.decode()
                rcv += d
                if "\r\n\r\n" in rcv:
                    print(f"[DEBUG] Request from {address}:\n{rcv}\n---")
                    hasil = httpserver.proses(rcv)
                    connection.sendall(hasil)
                    print(f"[DEBUG] Response sent to {address}")
                    rcv = ""
                    break
            else:
                break
        except OSError as e:
            print(f"[ERROR] Socket error: {e}")
            break
    connection.close()
    print(f"[DEBUG] Connection closed for {address}")

def Server():
    my_socket = socket(AF_INET, SOCK_STREAM)
    my_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8889))
    my_socket.listen(5)
    print("ProcessPool Server listening on port 8889")

    with ProcessPoolExecutor(20) as executor:
        while True:
            connection, address = my_socket.accept()
            executor.submit(ProcessTheClient, connection, address)

if __name__ == "__main__":
    Server()
