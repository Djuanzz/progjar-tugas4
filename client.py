import socket

def send_http_request(method, path, body=''):
    host = 'localhost'
    port = 8885

    request_line = f"{method} {path} HTTP/1.0\r\n"
    headers = "Host: localhost\r\n"
    if body:
        headers += f"Content-Length: {len(body.encode())}\r\n"
    headers += "Connection: close\r\n"

    full_request = request_line + headers + "\r\n" + body

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        client_socket.sendall(full_request.encode())

        response = b""
        while b"\r\n\r\n" not in response:
            response += client_socket.recv(1024)

        header_part, rest = response.split(b"\r\n\r\n", 1)
        headers = header_part.decode().split("\r\n")
        content_length = 0
        for line in headers:
            if line.lower().startswith("content-length"):
                content_length = int(line.split(":")[1].strip())

        body = rest
        while len(body) < content_length:
            body += client_socket.recv(1024)

        full_response = header_part + b"\r\n\r\n" + body
        print(full_response.decode(errors="ignore"))


def get_list():
    send_http_request("GET", "/list")

def upload_file(filename, content):
    body = f"{filename}\n{content}"
    send_http_request("POST", "/upload", body)

def delete_file(filename):
    path = f"/{filename}"
    send_http_request("DELETE", path)

def menu():
    while True:
        print("\n=== HTTP Client Menu ===")
        print("1. Lihat daftar file (/list)")
        print("2. Upload file")
        print("3. Hapus file")
        print("4. Keluar")
        choice = input("Pilih opsi: ")

        if choice == '1':
            get_list()
        elif choice == '2':
            filename = input("Masukkan nama file yang akan diupload: ")
            content = input("Masukkan isi file: ")
            upload_file(filename, content)
        elif choice == '3':
            filename = input("Masukkan nama file yang akan dihapus: ")
            delete_file(filename)
        elif choice == '4':
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    menu()
