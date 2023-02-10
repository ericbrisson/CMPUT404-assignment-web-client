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

# Modifications from original version:
# Copyright 2023 Eric Brisson

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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

    def __str__(self):
        return str(self.code) + "\n" + self.body


class HTTPClient(object):
    def get_host_port(self, url):
        # extract host and port
        parsed_url = urllib.parse.urlparse(url)

        # set host to netloc from parse
        if (parsed_url.netloc):
            self.host = parsed_url.netloc
        else:
            self.host = parsed_url.hostname

        # set port to port from parse
        if (parsed_url.port):
            self.port = parsed_url.port
        else:
            self.port = 80

        # set path from parse
        if (parsed_url.path):
            self.path = parsed_url.path
        else:
            self.path = "/"

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # split on every \r\n
        split_res = data.split("\r\n")

        # first element in split_req will contain HTTP version, responde code, and response title
        # parse out code, and return it
        return(int(split_res[0].split()[1]))

    def get_headers(self, data):
        # split on every \r\n
        split_res = data.split("\r\n")

        # will contain headers
        headers = {}
        for each_header in split_res[1:]:
            # once we see an empty line, we've reached the body
            if (each_header == ""):
                break

            header = each_header.split(":")[0].strip()
            value = each_header.split(":")[1].strip()
            headers[header] = value
        
        return headers

    def get_body(self, data):
        # split on every \r\n
        body = data.split('\r\n\r\n')[1]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # parse url
        self.get_host_port(url)

        # start building request byte string
        # begin request with GET and HTTP version 1.1
        request = 'GET ' + self.path + ' HTTP/1.1\r\n'

        # then, add Host header, for which the value is given to us in url param
        request += 'Host: ' + self.host + '\r\n'

        # then, add Connetion header, for which the value should be close
        request += 'Connection: close\r\n\r\n'

        # then connect, send, receive, and close
        self.connect(self.host, self.port)
        self.sendall(request)
        response = self.recvall()
        self.close()

        return HTTPResponse(self.get_code(response), self.get_body(response))

    def POST(self, url, args=None):
        # parse url
        self.get_host_port(url)

        # start building request byte string
        # begin request with GET and HTTP version 1.1
        request = 'POST ' + self.path + ' HTTP/1.1\r\n'

        # then, add Host header, for which the value is given to us in url param
        request += 'Host: ' + self.host + '\r\n'

        # the, add the Content-Type header, for which only application/x-www-form-urlencoded is supported
        request += 'Content-Type: ' + 'application/x-www-form-urlencoded' + '\r\n'

        # then, prepare body
        if (args):
            body = urllib.parse.urlencode(args)
            content_length = len(body)
        else:
            body = " "
            content_length = 0

        # then, add Content-Length header
        request += "Content-Length: " + str(content_length) + "\r\n"
        
        # then, add Connection header, for which the value should be close
        request += 'Connection: close\r\n\r\n' # add extra \r\n to seperate body

        # then, add body
        if (args):
            request += body # don't need \r\n here

        # then connect, send, receive, and close
        self.connect(self.host, self.port)
        self.sendall(request)
        response = self.recvall()
        self.close()

        return HTTPResponse(self.get_code(response), self.get_body(response))

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
