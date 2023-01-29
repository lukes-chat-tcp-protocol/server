import base64
import auth_mgmt

auth = auth_mgmt.AuthenticationManagement()

class handleToMode:
    def __init__(self, sock, addr, mode, comms):
        self.sock = sock
        self.comms = comms
        self.mode = mode
        self.addr = addr
        print('New connection from {} with mode {}'.format(addr[0], mode))
        client_env = {
            'login': False,
            'permission_level': None,
            'mode': mode,
        }
        self.comms.send(self.sock, client_env, b'READY')
        while True:
            try:
                recv = self.comms.recv(self.sock, client_env, 1024).decode('utf-8')
            except UnicodeDecodeError:
                self.comms.send(self.sock, client_env, b'ERROR InvalidCommand')
            else:
                args = recv.split(' ')
                resp = self.process_command(args, client_env)
                if resp == 'break':
                        break
                else:
                    client_env = resp

        self.sock.close()
    
    def process_command(self, args, client_env):
        def check_login(permission_level):
            if client_env['login']:
                if client_env['permission_level'] >= permission_level:
                    return True
                else:
                    self.comms.send(self.sock, client_env, b'ERROR PermissionDenied')
            else:
                self.comms.send(self.sock, client_env, b'ERROR LoginRequired')
                return False
        if args[0] == 'CLOSE':
            return 'break'
        elif args[0] == 'LOGIN':
            try:
                username = base64.b64decode(args[1]).decode('utf-8')
                password = base64.b64decode(args[2]).decode('utf-8')
            except IndexError:
                self.comms.send(self.sock, client_env, b'ERROR InvalidCommand')
            except Exception as e:
                print(str(e))
                self.comms.send(self.sock, client_env, b'ERROR InvalidB64Code')
            else:
                auth_attempt = auth.login(username, password)
                if auth_attempt == False:
                    self.comms.send(self.sock, client_env, b'ERROR LoginFailed')
                else:
                    self.comms.send(self.sock, client_env, b'ACK')
                    client_env['login'] = True
                    client_env['permission_level'] = auth_attempt

            return client_env
        elif args[0] == 'CONSOLE_LOG':
            if check_login(3):
                try:
                    print(base64.b64decode(args[1].encode()).decode('utf-8'))
                except IndexError:
                    self.comms.send(self.sock, client_env, b'ERROR InvalidCommand')
                except:
                    self.comms.send(self.sock, client_env, b'ERROR InvalidB64Code')
                else:
                    self.comms.send(self.sock, client_env, b'ACK')
        else:
            self.comms.send(self.sock, client_env, b'ERROR InvalidCommand')
        return client_env
