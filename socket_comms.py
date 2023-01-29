import socket
import threading
import base64
import auth_mgmt
import ssl

auth = auth_mgmt.AuthenticationManagement()

class SocketCommunication:
    def __init__(self, args):
        if args.insecure:
            print('WARNING! Running in insecure mode. Only do this if this is a development enviorment.')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            if args.key == None:
                self.ssl_context.load_cert_chain(certfile=args.cert)
            else:
                self.ssl_context.load_cert_chain(certfile=args.cert, keyfile=args.key)
            self.sock = self.ssl_context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.bind_address = args.bind_address
        self.port = args.port
        self.conns = []
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def start_server(self):
        self.sock.bind((self.bind_address, self.port))
        self.sock.listen(0)
        print('Listening for connections on {}:{}'.format(self.bind_address, self.port))
        while True:
            conn, addr = self.sock.accept()
            threading.Thread(target=self.handle_connection, args=[conn, addr]).start()
    
    def send(self, conn, client_env, data):
        if client_env['mode'].endswith('_TELNET'):
            conn.send(data + b'\r\n')
        else:
            conn.send(data)
    def recv(self, conn, client_env, size):
        if client_env['mode'].endswith('_TELNET'):
            data = conn.recv(size).replace(b'\r', b'').replace(b'\n', b'')
        else:
            data = conn.recv(size)
        return data
    def process_command(self, args, client_env, conn):
        def check_login(permission_level):
            if client_env['login']:
                if client_env['permission_level'] >= permission_level:
                    return True
                else:
                    self.send(conn, client_env, b'ERROR PermissionDenied')
            else:
                self.send(conn, client_env, b'ERROR LoginRequired')
                return False
        if args[0] == 'CLOSE':
            return 'break'
        elif args[0] == 'LOGIN':
            try:
                username = base64.b64decode(args[1]).decode('utf-8')
                password = base64.b64decode(args[2]).decode('utf-8')
            except IndexError:
                self.send(conn, client_env, b'ERROR InvalidCommand')
            except:
                self.send(conn, client_env, b'ERROR InvalidB64Code')
            else:
                auth_attempt = auth.login(username, password)
                if auth_attempt == False:
                    self.send(conn, client_env, b'ERROR LoginFailed')
                else:
                    self.send(conn, client_env, b'ACK')
                    client_env['login'] = True
                    client_env['permission_level'] = auth_attempt

            return client_env
        elif args[0] == 'CONSOLE_LOG':
            if check_login(3):
                try:
                    print(base64.b64decode(args[1].encode()).decode('utf-8'))
                except IndexError:
                    self.send(conn, client_env, b'ERROR InvalidCommand')
                except:
                    self.send(conn, client_env, b'ERROR InvalidB64Code')
                else:
                    self.send(conn, client_env, b'ACK')
        else:
            self.send(conn, client_env, b'ERROR InvalidCommand')
            print(args)
        return client_env
    def handle_connection(self, conn, addr):
        self.conns.append({
            'conn_obj': conn,
            'address': addr[0]
        })
        conn.send(b'SEND_MODE ')
        try:
            mode = conn.recv(1024).decode('utf-8').replace('\n', '').replace('\r', '')
        except UnicodeDecodeError:
            conn.close()
        else:
            print('New connection from {} with mode {}'.format(addr[0], mode))
            client_env = {
                'login': False,
                'permission_level': None,
                'mode': mode,
            }
            self.send(conn, client_env, b'READY')
            while True:
                try:
                    recv = self.recv(conn, client_env, 1024).decode('utf-8')
                except UnicodeDecodeError:
                    self.send(conn, client_env, b'ERROR InvalidCommand')
                else:
                    args = recv.split(' ')
                    resp = self.process_command(args, client_env, conn)
                    if resp == 'break':
                        break
                    else:
                        client_env = resp

            conn.close()
