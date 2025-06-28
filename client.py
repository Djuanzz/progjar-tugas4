import socket

def send_request(host, port, request):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(request.encode())
    response = b""
    while True:
        data = s.recv(1024)
        if not data:
            break
        response += data
    s.close()
    print(response.decode())

if __name__ == "__main__":
    # Example GET
    print("==== GET /files ====")
    send_request("localhost", 8888, "GET /files HTTP/1.1\r\nHost: localhost\r\n\r\n")

    # Example POST (upload .txt)
    print("==== POST /upload ====")
    txt = "Ini isi file contoh.txt"
    req = f"POST /upload HTTP/1.1\r\nHost: localhost\r\nContent-Type: text/plain\r\nContent-Length: {len(txt)}\r\nX-Filename: contoh.txt\r\n\r\n{txt}"
    send_request("localhost", 8888, req)

    # Example DELETE
    # print("==== DELETE /files/contoh.txt ====")
    # send_request("localhost", 8888, "DELETE /files/contoh.txt HTTP/1.1\r\nHost: localhost\r\n\r\n")
