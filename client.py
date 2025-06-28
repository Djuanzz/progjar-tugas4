import sys
import socket
import json
import logging
import os

server_address = ('localhost', 8885)  

def make_socket(destination_address='localhost', port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.error(f"Error creating socket or connecting: {str(ee)}")
        return None


def send_command(command_str):
    alamat_server = server_address[0]
    port_server = server_address[1]
    sock = make_socket(alamat_server, port_server)

    if sock is None:
        logging.error("Failed to create socket, cannot send command.")
        return False

    logging.warning(f"Sending message to {server_address}")
    try:
        sock.sendall(command_str.encode())
        logging.warning(f"Sent:\n{command_str.strip()}") 

        data_received = b""
        headers_complete = False
        content_length = 0
        body_start_index = -1
        
        while True:
            data = sock.recv(1024)
            if not data:
                break 

            data_received += data

            if not headers_complete:
                header_end_marker = data_received.find(b"\\r\\n\\r\\n")
                if header_end_marker != -1:
                    headers_complete = True
                    headers_raw = data_received[:header_end_marker].decode('utf-8', errors='ignore')
                    body_start_index = header_end_marker + 4

                    for line in headers_raw.split('\\r\\n'):
                        if line.lower().startswith("content-length:"):
                            try:
                                content_length = int(line.split(':')[1].strip())
                                break
                            except ValueError:
                                content_length = 0 

            if headers_complete:
                current_body_length = len(data_received) - body_start_index
                if content_length > 0 and current_body_length >= content_length:
                    break
                elif content_length == 0 and header_end_marker != -1:
                    if not data:
                        break
            
        sock.close()
        
        logging.warning("Data received from server:")
        
        if headers_complete and body_start_index != -1:
            message_body = data_received[body_start_index:].decode('utf-8', errors='ignore')
            return message_body
        else:
            return data_received.decode('utf-8', errors='ignore')

    except Exception as ee:
        logging.error(f"Error during data sending or receiving: {str(ee)}")
        if sock:
            sock.close()
        return False


if __name__ == '__main__':
    print("\\n--- Testing Client Requests ---")

    # GET request to /
    cmd_get_root = "GET / HTTP/1.0\\r\\n\\r\\n"
    response_get_root = send_command(cmd_get_root)
    print("=== GET / ===")
    print(response_get_root)

    # GET request to /list
    cmd_get_list = "GET /list HTTP/1.0\\r\\n\\r\\n"
    response_get_list = send_command(cmd_get_list)
    print("=== GET /list ===")
    print(response_get_list)

    # GET request to /santai
    cmd_get_santai = "GET /santai HTTP/1.0\\r\\n\\r\\n"
    response_get_santai = send_command(cmd_get_santai)
    print("=== GET /santai ===")
    print(response_get_santai)

    # # POST request to /upload
    # filename = "test_upload_from_client.txt"
    # content = "This is a test upload from the Python client. It's a fantastic day for programming!"
    # post_data = urlencode({'filename': filename, 'content': content})
    # cmd_post_upload = (
    #     f"POST /upload HTTP/1.0\\r\\n"
    #     f"Content-Type: application/x-www-form-urlencoded\\r\\n"
    #     f"Content-Length: {len(post_data)}\\r\\n"
    #     f"\\r\\n" # Important blank line separating headers from body
    #     f"{post_data}"
    # )
    # response_post_upload = send_command(cmd_post_upload)
    # print("\\n=== POST /upload ===")
    # print(response_post_upload)

    # # GET request for the uploaded file (optional, to verify upload)
    # cmd_get_uploaded_file = f"GET /{filename} HTTP/1.0\\r\\n\\r\\n"
    # response_get_uploaded_file = send_command(cmd_get_uploaded_file)
    # print(f"\\n=== GET /{filename} (Verify Upload) ===")
    # print(response_get_uploaded_file)

    # # GET request to /delete the uploaded file
    # cmd_get_delete = f"GET /delete?file={filename} HTTP/1.0\\r\\n\\r\\n"
    # response_get_delete = send_command(cmd_get_delete)
    # print("\\n=== GET /delete ===")
    # print(response_get_delete)

    # # GET request to /video (this will be a redirect)
    # cmd_get_video = "GET /video HTTP/1.0\\r\\n\\r\\n"
    # response_get_video = send_command(cmd_get_video)
    # print("\\n=== GET /video ===")
    # print(response_get_video)

    # # GET request for a non-existent file
    # cmd_get_non_existent = "GET /nonexistent.txt HTTP/1.0\\r\\n\\r\\n"
    # response_get_non_existent = send_command(cmd_get_non_existent)
    # print("\\n=== GET /nonexistent.txt (404 Test) ===")
    # print(response_get_non_existent)