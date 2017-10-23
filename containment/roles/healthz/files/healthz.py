from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import sys


def serve(port, state):
    print('reading from {}'.format(state))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            message = 'healthz uninitialized'
            try:
                with open(state, 'r') as f:
                    lines = f.readlines()
                    for l in reversed(lines):
                        s = l.strip()
                        if len(s) > 0:
                            message = s
                            break
            except:
                message = 'healthz error'
            print('sending: {}'.format(message))
            rendered = bytes(message, 'utf-8')
            self.send_response(200)
            self.send_header('Content-Type','text/plain')
            self.send_header('Content-Length', len(rendered))
            self.end_headers()
            self.wfile.write(rendered)

    address = ('0.0.0.0', port)
    httpd = HTTPServer(address, Handler)
    print('serving on port {}'.format(port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


def main():
    if len(sys.argv) != 3:
        raise Exception('USE: {} [PORT] [STATE]'.format(sys.argv[0]))
    port = int(sys.argv[1])
    state = sys.argv[2]
    serve(port, state)


if __name__ == '__main__':
    main()
