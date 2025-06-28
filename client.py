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
    print("\n[RESPON DARI SERVER]:")
    print(response.decode())
    print("="*60 + "\n")

def menu():
    print("==== MENU CLIENT HTTP ====")
    print("1. Lihat daftar file di server")
    print("2. Upload file .txt")
    print("3. Hapus file dari server")
    print("4. Keluar")

def main():
    host = "localhost"
    port = 8888

    while True:
        menu()
        pilihan = input("Pilih menu (1-4): ").strip()

        if pilihan == "1":
            print("\n==== GET /files ====")
            send_request(host, port, "GET /files HTTP/1.1\r\nHost: localhost\r\n\r\n")

        elif pilihan == "2":
            print("\n==== UPLOAD FILE TXT ====")
            filename = input("Nama file (.txt): ").strip()
            if not filename.endswith(".txt"):
                print("Hanya file .txt!\n")
                continue
            print("Masukkan isi file (akhiri dengan baris kosong):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            content = "\n".join(lines)

            req = (
                f"POST /upload HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(content)}\r\n"
                f"X-Filename: {filename}\r\n"
                f"\r\n"
                f"{content}"
            )
            send_request(host, port, req)

        elif pilihan == "3":
            print("\n==== HAPUS FILE ====")
            filename = input("Nama file yang akan dihapus (contoh: data.txt): ").strip()
            req = f"DELETE /files/{filename} HTTP/1.1\r\nHost: {host}\r\n\r\n"
            send_request(host, port, req)

        elif pilihan == "4":
            print("Keluar.")
            break

        else:
            print("Pilihan tidak valid. Silakan coba lagi.\n")

if __name__ == "__main__":
    main()
