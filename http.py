import os
from glob import glob
from datetime import datetime

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html'
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append(f"HTTP/1.0 {kode} {message}\r\n")
        resp.append(f"Date: {tanggal}\r\n")
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append(f"Content-Length: {len(messagebody)}\r\n")
        for kk in headers:
            resp.append(f"{kk}:{headers[kk]}\r\n")
        resp.append("\r\n")

        response_headers = ''.join(resp)

        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        return response_headers.encode() + messagebody

    def proses(self, data):
        requests = data.split("\r\n")
        if not requests or len(requests[0].split(" ")) < 2:
            return self.response(400, 'Bad Request', 'Malformed request')

        method, object_address = requests[0].split(" ")[:2]
        all_headers = [n for n in requests[1:] if n != '']

        try:
            if method.upper() == 'GET':
                return self.http_get(object_address, all_headers)
            elif method.upper() == 'POST':
                return self.http_post(object_address, all_headers)
            else:
                return self.response(400, 'Bad Request', '', {})
        except Exception as e:
            return self.response(500, 'Internal Server Error', str(e), {})

    def http_get(self, object_address, headers):
        thedir = './'

        if object_address == '/':
            return self.response(200, 'OK', 'Ini Adalah Web Server Percobaan', {})

        if object_address == '/list':
            file_list = os.listdir(thedir)
            list_text = "\n".join(file_list)
            return self.response(200, 'OK', list_text, {'Content-Type': 'text/plain'})

        object_address = object_address[1:]
        filepath = os.path.join(thedir, object_address)

        if not os.path.exists(filepath):
            return self.response(404, 'Not Found', 'File tidak ditemukan', {})

        with open(filepath, 'rb') as fp:
            isi = fp.read()

        fext = os.path.splitext(filepath)[1]
        content_type = self.types.get(fext, 'application/octet-stream')
        headers = {'Content-Type': content_type}
        return self.response(200, 'OK', isi, headers)

    def http_post(self, object_address, headers):
        if object_address == '/upload':
            try:
                body = headers[-1]
                parts = body.split("\n", 1)
                if len(parts) != 2:
                    return self.response(400, 'Bad Request', 'Format upload salah')

                filename = parts[0].strip()
                content = parts[1]

                with open(filename, 'w') as f:
                    f.write(content)

                return self.response(200, 'OK', f'File {filename} berhasil diupload', {})
            except Exception as e:
                return self.response(500, 'Internal Server Error', str(e), {})

        elif object_address == '/delete':
            try:
                filename = headers[-1].strip()
                if not os.path.exists(filename):
                    return self.response(404, 'Not Found', 'File tidak ditemukan', {})
                os.remove(filename)
                return self.response(200, 'OK', f'File {filename} berhasil dihapus', {})
            except Exception as e:
                return self.response(500, 'Internal Server Error', str(e), {})

        else:
            return self.response(400, 'Bad Request', 'Perintah POST tidak dikenali', {})
