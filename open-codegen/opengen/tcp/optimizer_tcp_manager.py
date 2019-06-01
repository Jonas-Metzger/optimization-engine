import yaml, os, subprocess, socket, json
from threading import Thread
from retry import retry


class OptimizerTcpManager:

    def __init__(self, optimizer_path):
        self.__optimizer_path = optimizer_path
        self.__tcp_details = None

    def __load_tcp_details(self):
        yaml_file = os.path.join(self.__optimizer_path, "optimizer.yml")
        with open(yaml_file, 'r') as stream:
            self.__tcp_details = yaml.safe_load(stream)

    def __threaded_start(self):
        command = ['cargo', 'run']
        p = subprocess.Popen(command, cwd=self.__optimizer_path)
        p.wait()

    @retry(tries=10, delay=1)
    def __obtain_socket_connection(self):
        tcp_data = self.__tcp_details
        ip = tcp_data['tcp']['ip']
        port = tcp_data['tcp']['port']
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        return s

    def __ping(self, s):
        ping_message = b'{"Ping" : 1}'
        s.sendall(ping_message)
        data = s.recv(256)  # 256 is more than enough
        return data.decode()

    def ping(self):
        s = self.__obtain_socket_connection()
        data = self.__ping(s)
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return data

    def start(self):
        self.__load_tcp_details()
        thread = Thread(target=self.__threaded_start)

        # start the server
        thread.start()

        # ping the server until it responds so that we know it's
        # up and running
        pong = self.ping()

    def __kill(self, s):
        ping_message = b'{"Kill" : 1}'
        s.sendall(ping_message)

    def kill(self):
        s = self.__obtain_socket_connection()
        self.__kill(s)
        s.shutdown(socket.SHUT_RDWR)
        s.close()

    def __call(self, p, s, buffer_len=1024):
        run_message = '{"Run" : {"parameter": ['
        parameter_comma_separated_list = ','.join(map(str, p))
        run_message += parameter_comma_separated_list
        run_message += ']}}'

        s.sendall(run_message.encode())
        data = s.recv(buffer_len)  # 256 is more than enough
        return data.decode()

    def call(self, p, buffer_len=1024):
        s = self.__obtain_socket_connection()
        result = self.__call(p, s, buffer_len)
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return result
