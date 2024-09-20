"""Servidor Cliente"""
import socket
import os.path


class TCPClient:
    """
    Classe responsável por criar um cliente TCP que se conecta a um servidor
    para enviar dados e receber uma resposta.
    """

    def __init__(self, host=None, port=None, message_limit=None):
        """
        Inicializa o cliente TCP.

        Parâmetros:
        - host (str): Endereço IP do servidor para o qual o cliente se conectará. Default: '127.0.0.1'.
        - port (int): Porta na qual o cliente tentará se conectar. Default: 5784.
        - message_limit (int): Tamanho máximo dos dados recebidos. Default: 1024.
        """
        # Obter valores de ambiente ou usar valores padrão
        self.host = host or os.getenv('HOST', '127.0.0.1')
        self.port = int(port or os.getenv('PORT', 5784))
        self.max_limit_message = int(message_limit or os.getenv('MAX_LIMIT_MESSAGE', 1024))

        # Inicializa o socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_data(self, data):
        """
        Conecta ao servidor e envia dados. Aguarda a resposta do servidor e a imprime.

        Parâmetros:
        - data (str): Dados a serem enviados ao servidor.
        """
        # Cria um socket TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))  # Conecta ao servidor
            s.sendall(data.encode('utf-8'))  # Envia os dados codificados
            response = s.recv(1024).decode('utf-8')  # Recebe a resposta do servidor
            print('{}'.format(response))  # Exibe a resposta

    def stop_client(self):
        """
        Comentários
        :return:
        """
        command = input()
        if command.lower() == 'parar':
            print('Encerrando conexão')
            self.client_socket.close()


# Inicializando o cliente
if __name__ == "__main__":
    # Cria uma instância do cliente TCP
    client = TCPClient()

    # Exemplo de dados válidos a serem enviados
    # dados = "joao,joao@nimbusmeteorologia.com.br,01234567891,30"
    dados = "joao,joao@nimbusmeteorologia.com.br,01234567891"
    client.send_data(dados)
