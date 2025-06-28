import sys
import os.path
import uuid
from glob import glob
from datetime import datetime
import json
import urllib.parse

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.json': 'application/json'
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = [
            f"HTTP/1.0 {kode} {message}\r\n",
            f"Date: {tanggal}\r\n",
            "Connection: close\r\n",
            "Server: myserver/1.0\r\n",
            f"Content-Length: {len(messagebody)}\r\n"
        ]
        for kk in headers:
            resp.append(f"{kk}: {headers[kk]}\r\n")
        resp.append("\r\n")

        response_headers = ''.join(resp)

        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        return response

    def proses(self, data):
        requests = data.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n != '']

        request_body = ""
        if "\r\n\r\n" in data:
            body_start = data.find("\r\n\r\n") + 4
            request_body = data[body_start:]

        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip()
            if method == 'GET':
                return self.http_get(object_address, all_headers)
            elif method == 'POST':
                return self.http_post(object_address, all_headers, request_body)
            elif method == 'DELETE':
                return self.http_delete(object_address, all_headers)
            else:
                return self.response(400, 'Bad Request', '', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})

    def http_get(self, object_address, headers):
        files = glob('./*')
        thedir = './'

        if object_address == '/':
            return self.response(200, 'OK', 'Ini Adalah web Server percobaan', {})

        if object_address == '/video':
            return self.response(302, 'Found', '', {'Location': 'https://youtu.be/katoxpnTf04'})

        if object_address == '/santai':
            return self.response(200, 'OK', 'santai saja', {})

        if object_address == '/files' or object_address.startswith('/files/'):
            return self.list_files(object_address)

        object_address = object_address[1:]
        if thedir + object_address not in files:
            return self.response(404, 'Not Found', '', {})

        with open(thedir + object_address, 'rb') as fp:
            isi = fp.read()

        fext = os.path.splitext(thedir + object_address)[1]
        content_type = self.types.get(fext, 'application/octet-stream')

        return self.response(200, 'OK', isi, {'Content-Type': content_type})

    def http_post(self, object_address, headers, request_body):
        if object_address.startswith('/upload'):
            return self.upload_file(request_body, headers)
        return self.response(200, 'OK', 'kosong', {})

    def http_delete(self, object_address, headers):
        if object_address.startswith('/files/'):
            filename = object_address[7:]
            return self.delete_file(filename)
        else:
            return self.response(400, 'Bad Request', 'Invalid delete path', {})

    def list_files(self, object_address):
        try:
            target_dir = './' if object_address == '/files' else './' + object_address[7:]
            if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
                return self.response(404, 'Not Found', 'Directory not found', {})

            files = os.listdir(target_dir)
            return self.response(200, 'OK', json.dumps(files), {'Content-Type': 'application/json'})
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Error listing files: {str(e)}', {})

    def upload_file(self, request_body, headers):
        try:
            content_type_header = None
            for header in headers:
                if header.lower().startswith('content-type:'):
                    content_type_header = header
                    break

            if not content_type_header or 'multipart/form-data' not in content_type_header:
                filename = f"uploaded_file_{uuid.uuid4().hex[:8]}.txt"

                for header in headers:
                    if header.lower().startswith('x-filename:'):
                        filename = header.split(':')[1].strip()
                        break

                if not filename.endswith('.txt'):
                    return self.response(400, 'Bad Request', 'Only .txt files are allowed', {})

                with open('./' + filename, 'w') as f:
                    f.write(request_body)

                response_data = {
                    'status': 'success',
                    'message': f'File {filename} uploaded successfully',
                    'filename': filename
                }
                return self.response(201, 'Created', json.dumps(response_data), {'Content-Type': 'application/json'})
            else:
                return self.response(400, 'Bad Request', 'Multipart upload not supported', {})
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Upload error: {str(e)}', {})

    def delete_file(self, filename):
        try:
            file_path = './' + filename
            if not os.path.exists(file_path):
                return self.response(404, 'Not Found', f'File {filename} not found', {})
            if os.path.isdir(file_path):
                return self.response(400, 'Bad Request', 'Cannot delete directory', {})
            os.remove(file_path)
            response_data = {
                'status': 'success',
                'message': f'File {filename} deleted successfully',
                'filename': filename
            }
            return self.response(200, 'OK', json.dumps(response_data), {'Content-Type': 'application/json'})
        except PermissionError:
            return self.response(403, 'Forbidden', 'Permission denied to delete file', {})
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Delete error: {str(e)}', {})

# TESTING
if __name__ == "__main__":
    httpserver = HttpServer()

    print("1. GET /files:")
    cmd = "GET /files HTTP/1.1\r\nHost: localhost\r\n\r\n"
    d = httpserver.proses(cmd)
    print(d.decode())
    print("=" * 50)

    print("2. Testing UPLOAD TXT FILE (Simple):")
    txt_content = "Ini file txt"
    content_length = len(txt_content)
    cmd = f"""POST /upload HTTP/1.1\r
    Host: localhost\r
    Content-Type: text/plain\r
    Content-Length: {content_length}\r
    X-Filename: data_upload.txt\r
    \r
    {txt_content}"""
    d = httpserver.proses(cmd)
    print(d.decode())
    print("=" * 50)

    print("3. Testing DELETE FILE:")
    cmd = "DELETE /files/data_upload.txt HTTP/1.1\r\nHost: localhost\r\n\r\n"
    d = httpserver.proses(cmd)
    print(d.decode())
    print("=" * 50)
