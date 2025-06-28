from socket import *
import socket
import time
import sys
import logging
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    logging.warning(f"Connection from {address}")
    rcv = ""
    try:
        while True:
            data = connection.recv(1024)
            if data:
                d = data.decode('utf-8', errors='ignore')
                rcv = rcv + d
                if "\\r\\n\\r\\n" in rcv:
                    logging.warning(f"Received from client {address}:\n{rcv.strip()}")
                    
                    hasil = httpserver.proses(rcv)
                    
                    connection.sendall(hasil)
                    
                    break 
            else:
                break
    except Exception as e:
        logging.error(f"Error processing client {address}: {str(e)}")
    finally:
        logging.warning(f"Closing connection from {address}")
        connection.close() 


def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_port = 8885 
    my_socket.bind(('0.0.0.0', server_port))
    my_socket.listen(5) 

    logging.warning(f"Server listening on port {server_port}")

    with ThreadPoolExecutor(max_workers=20) as executor:
        while True:
            try:
                connection, client_address = my_socket.accept()
                p = executor.submit(ProcessTheClient, connection, client_address)
                the_clients.append(p)
                
                the_clients = [f for f in the_clients if not f.done()]
                logging.info(f"Currently active client handlers: {len(the_clients)}")
            except KeyboardInterrupt:
                logging.warning("Server shutting down due to Ctrl+C.")
                break
            except Exception as e:
                logging.error(f"Error in server accept loop: {str(e)}")
    
    my_socket.close()
    logging.warning("Server socket closed.")


def main():
    Server()

if __name__ == "__main__":
    main()