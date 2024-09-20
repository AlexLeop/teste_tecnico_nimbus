""" Teste para comunicação de Servidores TCP/IP entre cliente e servidor """
import pytest
from unittest.mock import patch, MagicMock, mock_open
from conexao.server import TCPServer  # Supondo que o código do servidor está em 'tcp_server.py'


@pytest.fixture(scope='module')
def tcp_server():
    """
    Fixture que inicializa uma instância do TCPServer para ser usada nos testes.
    """
    return TCPServer()


def test_init_server(tcp_server):
    """
    Testa a inicialização do servidor com os valores padrão.
    """
    assert tcp_server.host == 'localhost'
    assert tcp_server.port == 5784
    assert tcp_server.works == 5
    assert tcp_server.max_limit_message == 1024


def test_validate_data_valid(tcp_server):
    """
    Testa a função validate_data com dados válidos.
    """
    data = "João,joao@example.com,1234567890,30"
    assert tcp_server.validate_data(data) is True


def test_validate_data_invalid(tcp_server):
    """
    Testa a função validate_data com dados inválidos.
    """
    data = "João,joao@example.com,1234567890"
    assert tcp_server.validate_data(data) is False


def test_save_data(tcp_server):
    """
    Testa a função save_data para garantir que os dados são salvos corretamente.
    Usa um mock para evitar a criação de um arquivo real e verifica se a função
    write do arquivo foi chamada corretamente.

    Parâmetros:
    - tcp_server: Instância do servidor TCP que contém a função save_data.
    """
    # Mock do 'open' para o caminho correto
    with patch("builtins.open", new_callable=mock_open) as mock_open_file:
        # Mock do arquivo retornado por 'open'
        mock_file = mock_open_file.return_value

        # Chama a função save_data
        tcp_server.save_data("João,joao@example.com,1234567890,30")

        # Verifica se open foi chamado com os argumentos corretos
        mock_open_file.assert_called_once_with("../relatorio/clientes.txt", "a")

        # Verifica se o método write foi chamado com os dados corretos
        mock_file.write.assert_called_once_with("João,joao@example.com,1234567890,30\n")


def test_handle_client_valid_data(tcp_server):
    """
    Testa o handle_client com dados válidos.
    Usa mocks para simular a comunicação via socket.
    """
    mock_socket = MagicMock()
    mock_socket.recv.return_value = "João,joao@example.com,1234567890,30".encode('utf-8')

    with patch.object(tcp_server, 'save_data') as mock_save_data, \
         patch.object(tcp_server, 'validate_data', return_value=True):
        tcp_server.handle_client(mock_socket)

        mock_socket.sendall.assert_called_once_with('Ok'.encode('utf-8'))
        mock_save_data.assert_called_once_with("João,joao@example.com,1234567890,30")


def test_handle_client_invalid_data(tcp_server):
    """
    Testa o handle_client com dados inválidos.
    Usa mocks para simular a comunicação via socket.
    """
    mock_socket = MagicMock()
    mock_socket.recv.return_value = "João,joao@example.com,1234567890".encode('utf-8')

    with patch.object(tcp_server, 'validate_data', return_value=False):
        tcp_server.handle_client(mock_socket)

        mock_socket.sendall.assert_called_once_with('Erro: Formato inválido'.decode('utf-8'))
