#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))


    def get_code(self, data):
        # status code is the second object in http response
        return int(data.split()[1])

    def get_headers(self,data):
        # request header ends with \r\n
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[-1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    def build_request(self, method, parsed, args=None):
        """Build Http request.
        Parameters:
            method -> A string indicating the HTTP/1.1 method used
            parsed -> Parsed url
            args(optional) -> A dictionary to url encode in the body
                of the request.

        Returns: HTTPRequest Object
        """
        if args:
            query = urllib.parse.urlencode(args)
            length = max(len(query), 8)
        else:
            query = ''
            length = 9

        if parsed.path == '':
            path = '/'
        else:
            path = parsed.path

        if method == 'GET':
            req = '''GET {} HTTP/1.1\r\nAccept-Encoding: identity\r
Host: {}\r\nUser-Agent: Python-urllib/3.7\r\nConnection: close\r\n\r\n'''.format(path, parsed.hostname)

        elif method == 'POST':
            req = '''POST {} HTTP/1.1\r\nAccept-Encoding: identity\r
Content-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r
Host: {}\r\nUser-Agent: Python-urllib/3.7\r\nConnection: close\r\n\r\n{}'''.format(
            path, length, parsed.hostname, query
        )

        return req

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        """Basic GET request.
        Parameters:
            url -> A string of the target resorce. ie. "http://www.cs.ualberta.ca/"
            args(optional) -> A dictionary to url encode in the body
                of the request.
        Returns: HTTPRequest Object
        """
        parsed = urllib.parse.urlparse(url)

        if parsed.port is None:
            port = 80
        else:
            port = parsed.port

        self.connect(parsed.hostname, port)
        req = self.build_request('GET', parsed)
        self.sendall(req)

        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)

        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        parsed = urllib.parse.urlparse(url)

        if parsed.port is None:
            port = 80
        else:
            port = parsed.port

        self.connect(parsed.hostname, port)

        req = self.build_request('POST', parsed, args)

        self.sendall(req)

        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)

        self.close()
        return HTTPResponse(code, body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
