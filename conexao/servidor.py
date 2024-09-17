import socket
import threading


class IniciarServidor:
    """
    Class responsável por inicializar um servidor TCP/IP

    :param:
    - host(str) : Endereço de conexão do servidor
    - port(int) : Porta utilizada pelo servidor para recepcionar e enviar dados
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_running = threading.Event()
        self.socket_running.set()

    def iniciar(self):
        """
        Inicializa o servidor
        """
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print('Servidor iniciado na porta {}...'.format(self.port))

        while self.socket_running.is_set():
            try:
                cliente, add = self.socket.accept()
                print('Conexão estabelecida com {}'.format(add))
            except Exception as e:
                if not self.socket_running.is_set():
                    break
                print('Erro ao aceitar conexão: {}'.format(e))
            self.socket.close()

    def escutar_cliente(self, cliente):
        """
        Responsável por recepcionar a mensagem do cliente, verificar se estão no formato correto e retornar um status
        :param cliente:
        :return:
        """
        while self.socket_running.is_set():
            dados = cliente.recv(1024).decode('utf-8')
            if not dados:
                break
            if self.validar_dados(dados):
                self.salvar(dados)
                cliente.sendall('Ok'.encode('utf-8'))
            else:
                cliente.sendall('Erro: Formato inválido'.encode('utf-8'))

    def validar_dados(self):
        """
        Modulo responsável por validar os dados enviados pelo cliente
        :return:
        """
        pass

    def salvar(self):
        """
        Modulo responsável por savar os dados enviados pelo cliente
        :return:
        """

        pass


if __name__ == "__main__":
    host = str(input('INFORME O SERVIDOR PARA CONEXÃO:\n'))
    port = int(input('INFORME A PORTA:\n'))
    servidor = IniciarServidor(host, port)
    servidor.iniciar()
