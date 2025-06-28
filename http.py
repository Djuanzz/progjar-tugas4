import sys
import os
import uuid
from glob import glob
from datetime import datetime
from urllib.parse import unquote_plus, parse_qs

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.txt': 'text/plain',
            '.html': 'text/html'
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append("HTTP/1.0 {} {}\r\n".format(kode, message))
        resp.append("Date: {}\r\n".format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n".format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n".format(kk, headers[kk]))
        resp.append("\r\n")

        response_headers = ''.join(resp)
        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        return response_headers.encode() + messagebody

    def proses(self, data):
        requests = data.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n != '']
        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip()
            if method == 'GET':
                return self.http_get(object_address, all_headers)
            elif method == 'POST':
                body = data.split('\r\n\r\n', 1)[-1]
                return self.http_post(object_address, all_headers, body)
            else:
                return self.response(400, 'Bad Request', '', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})

    def http_get(self, object_address, headers):
        thedir = './'

        if object_address == '/':
            return self.response(200, 'OK', 'Ini Adalah web Server percobaan', {})

        elif object_address == '/list':
            files = os.listdir(thedir)
            file_list = '\n'.join(files)
            return self.response(200, 'OK', file_list, {'Content-type': 'text/plain'})

        elif object_address.startswith('/delete'):
            query = object_address.split('?', 1)[-1]
            params = parse_qs(query)
            filename = params.get('file', [None])[0]
            if filename:
                filepath = os.path.join(thedir, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    return self.response(200, 'OK', f"File {filename} berhasil dihapus", {})
                else:
                    return self.response(404, 'Not Found', f"File {filename} tidak ditemukan", {})
            else:
                return self.response(400, 'Bad Request', "Parameter 'file' tidak ada", {})

        elif object_address == '/video':
            return self.response(302, 'Found', '', {'Location': 'https://youtu.be/katoxpnTf04'})

        elif object_address == '/santai':
            return self.response(200, 'OK', 'santai saja', {})

        else:
            filepath = thedir + object_address.lstrip('/')
            if not os.path.exists(filepath):
                return self.response(404, 'Not Found', 'File tidak ditemukan', {})
            with open(filepath, 'rb') as fp:
                isi = fp.read()
            fext = os.path.splitext(filepath)[1]
            content_type = self.types.get(fext, 'application/octet-stream')
            headers = {'Content-type': content_type}
            return self.response(200, 'OK', isi, headers)

    def http_post(self, object_address, headers, body):
        thedir = './'
        if object_address == '/upload':
            try:
                # Format body: filename=example.txt&content=isi+file+contoh
                data = parse_qs(body)
                filename = data.get('filename', [None])[0]
                content = data.get('content', [''])[0]
                if filename:
                    filepath = os.path.join(thedir, filename)
                    with open(filepath, 'w') as f:
                        f.write(unquote_plus(content))
                    return self.response(200, 'OK', f"File {filename} berhasil diupload", {})
                else:
                    return self.response(400, 'Bad Request', "Parameter 'filename' tidak ditemukan", {})
            except Exception as e:
                return self.response(500, 'Internal Server Error', str(e), {})
        else:
            return self.response(404, 'Not Found', 'Endpoint tidak ditemukan', {})

# Contoh penggunaan
if __name__ == "__main__":
    server = HttpServer()

    print("=== GET File ===")
    print(server.proses("GET /testing.txt HTTP/1.0\r\n\r\n"))

    print("=== GET List ===")
    print(server.proses("GET /list HTTP/1.0\r\n\r\n"))

    print("=== POST Upload ===")
    upload_request = (
        "POST /upload HTTP/1.0\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "\r\n"
        "filename=baru.txt&content=ini+isi+file+baru"
    )
    print(server.proses(upload_request))

    # print("=== POST Delete ===")
    # print(server.proses("GET /delete?file=baru.txt HTTP/1.0\r\n\r\n"))
