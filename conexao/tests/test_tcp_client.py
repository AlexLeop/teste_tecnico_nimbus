import socket
import pytest
from unittest import mock
from conexao.client import TCPClient  # Importar a classe TCPClient do script original


@pytest.fixture
def mock_socket():
    """
    Um mock para o objeto socket para evitar conexões reais durante os testes.
    """
    with mock.patch('socket.socket') as mock_socket:
        yield mock_socket


def test_tcp_client_init(mock_socket):
    """
    Testa a inicialização do cliente TCP e verifica se o socket é criado corretamente.
    """
    # Criando uma instância do TCPClient com valores padrão
    client = TCPClient()

    # Verificando se o socket foi criado corretamente
    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
    assert client.host == 'localhost'
    assert client.port == 5784
    assert client.max_limit_message == 1024


def test_tcp_client_send_data(mock_socket):
    """
    Testa o envio de dados pelo cliente TCP.
    """
    # Criando uma instância do TCPClient
    client = TCPClient()

    # Dados a serem enviados
    data = "joao,joao@nimbusmeteorologia.com.br,01234567891,30"

    # Mock do socket
    mock_client_socket = mock_socket.return_value.__enter__.return_value
    mock_client_socket.recv.return_value = 'Ok'.encode('utf-8')  # Simulando resposta do servidor

    # Executando o método de envio de dados
    client.send_data(data)

    # Verificando se o cliente tentou se conectar ao servidor correto
    mock_client_socket.connect.assert_called_once_with(('localhost', 5784))

    # Verificando se os dados foram enviados corretamente
    mock_client_socket.sendall.assert_called_once_with(data.encode('utf-8'))

    # Verificando se a resposta do servidor foi recebida corretamente
    mock_client_socket.recv.assert_called_once_with(1024)


def test_tcp_client_send_data_custom_port(mock_socket):
    """
    Testa o envio de dados pelo cliente TCP com uma porta personalizada.
    """
    # Criando uma instância do TCPClient com uma porta personalizada
    client = TCPClient(port=9090)

    # Dados a serem enviados
    data = "maria,maria@nimbusmeteorologia.com.br,98765432100,25"

    # Mock do socket
    mock_client_socket = mock_socket.return_value.__enter__.return_value
    mock_client_socket.recv.return_value = 'Ok'.encode('utf-8')

    # Executando o método de envio de dados
    client.send_data(data)

    # Verificando se o cliente tentou se conectar ao servidor correto na porta personalizada
    mock_client_socket.connect.assert_called_once_with(('localhost', 9090))

    # Verificando se os dados foram enviados corretamente
    mock_client_socket.sendall.assert_called_once_with(data.encode('utf-8'))


def test_tcp_client_invalid_data(mock_socket):
    """
    Testa o envio de dados inválidos e a resposta do servidor.
    """
    client = TCPClient()

    # Dados inválidos a serem enviados
    data = "invalido"

    # Mock do socket
    mock_client_socket = mock_socket.return_value.__enter__.return_value
    mock_client_socket.recv.return_value = 'Erro: Formato inválido'.encode('utf-8')

    # Executando o método de envio de dados
    client.send_data(data)

    # Verificando se o cliente recebeu a resposta de erro
    mock_client_socket.sendall.assert_called_once_with(data.encode('utf-8'))
    mock_client_socket.recv.assert_called_once_with(1024)

