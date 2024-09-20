""" Servidor """
import os
import dotenv
import socket
import threading

dotenv.load_dotenv(dotenv.find_dotenv())


class TCPServer:
    """
    Classe responsável por criar um servidor TCP que escuta uma porta específica
    e trata as conexões de clientes, recebendo dados e respondendo conforme
    o formato esperado.
    """

    def __init__(self, host: str = None, port: int = None,
                 works: int = None, message_limit: int = None, close: str = None):
        """
        Inicializa o servidor TCP.

        Parâmetros:
        - host (str): Endereço IP onde o servidor vai rodar. Default: '127.0.0.1' (localhost).
        - port (int): Porta que o servidor vai escutar. Default: 5784.
        - works (int): Define a quantidade de conexões simultâneas. Default: 5.
        - message_limit (int): Tamanho máximo dos dados recebidos. Default: 1024.
        """
        # Obter valores de ambiente ou usar valores padrão
        self.host = host or os.getenv('HOST')
        self.port = int(port or os.getenv('PORT'))
        self.works = int(works or os.getenv('WORKS'))
        self.max_limit_message = int(message_limit or os.getenv('MAX_LIMIT_MESSAGE'))
        self.close = close

        # Inicializa o socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_running = threading.Event()
        self.server_running.set()

    def start(self):
        """
        Inicia o servidor, fazendo-o escutar na porta configurada.
        Aceita conexões de clientes e inicia uma nova thread para tratar cada um.
        """
        self.server_socket.bind((self.host, self.port))  # Vincula o socket ao endereço e porta
        self.server_socket.listen(self.works)  # Define o limite de 5 conexões simultâneas na fila de espera
        print('Servidor iniciado na porta {}...'.format(self.port))
        print('Digite "parar" para encerrar o servidor.\n')

        # Iniciar uma thread para aceitar o comando de parada
        stop_thread = threading.Thread(target=self.stop_server)
        stop_thread.start()

        while self.server_running.is_set():
            try:
                client_socket, addr = self.server_socket.accept()
                print('Conexão estabelecida com {}'.format(addr))
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.start()
            except Exception as e:
                if not self.server_running.is_set():
                    break
                print('Erro ao aceitar conexão: {}'.format(e))

    def handle_client(self, client_socket):
        """
        Trata a comunicação com um cliente, recebendo dados, validando-os e respondendo conforme necessário.

        Parâmetros:
        - client_socket (socket): O socket do cliente conectado.
        """
        while self.server_running.is_set():
            try:
                data = client_socket.recv(self.max_limit_message).decode('utf-8')
                if not data:
                    break

                if self.validate_data(data):
                    self.save_data(data)
                    client_socket.sendall('Ok'.encode())
                else:
                    client_socket.sendall('Erro: Formato inválido'.encode())

            except Exception as e:
                print('Erro: {}'.format(e))
                break
        client_socket.close()

    def stop_server(self):
        """
        Comentário
        """
        while self.server_running.is_set():
            command = input()
            if command.lower() == 'parar':
                print('encerrando servidor...')
                self.server_running.clear()
                self.server_socket.close()
                break

    @staticmethod
    def validate_data(data):
        """
        Valida os dados recebidos no formato: nome, e-mail, telefone, idade.

        Parâmetros:
        - data (str): Dados recebidos do cliente.

        Retorno:
        - bool: True se os dados estiverem no formato correto, false caso contrário.
        """
        try:
            nome, email, telefone, idade = data.split(',')
            return True
        except ValueError:
            return False

    @staticmethod
    def save_data(data):
        """
        Salva os dados recebidos em um arquivo de texto local.

        Parâmetros:
        - data (str): Dados validados a serem salvos.
        """
        with open("../relatorio/clientes.txt", "a") as f:
            f.write(data + '\n')  # Escreve os dados no arquivo, uma linha por dado


# Inicializando o servidor
if __name__ == "__main__":
    server = TCPServer()
    server.start()
