import pytest
import os
from relatorio.relatorios import RelatorioMeteorologico


# Teste para garantir que o conteúdo bruto é carregado corretamente
def test_carregar_bruto(tmp_path):
    # Cria um arquivo bruto temporário
    caminho_bruto = tmp_path / "bruto.txt"
    caminho_bruto.write_text(
        "2024-09-15T12:00 Chuva forte em várias regiões.\n2024-09-16T08:00 Neblina leve durante a manhã.")

    # Instancia a classe e carrega o conteúdo
    relatorio = RelatorioMeteorologico(telefones=["01234567891"], data="2024-09-15T00:00", envia_email=False,
                                       caminho_bruto=caminho_bruto)

    # Verifica se o conteúdo foi carregado corretamente
    assert relatorio.conteudo_bruto == [
        "2024-09-15T12:00 Chuva forte em várias regiões.\n",
        "2024-09-16T08:00 Neblina leve durante a manhã."
    ]


# Teste para garantir que as previsões são processadas corretamente
def test_processar_previsoes(tmp_path):
    # Cria um arquivo bruto temporário
    caminho_bruto = tmp_path / "bruto.txt"
    caminho_bruto.write_text(
        "2024-09-15T12:00 Chuva forte em várias regiões.\n2024-09-16T08:00 Neblina leve durante a manhã.")

    # Instancia a classe e processa as previsões
    relatorio = RelatorioMeteorologico(telefones=["01234567891"], data="2024-09-15T00:00", envia_email=False,
                                       caminho_bruto=caminho_bruto)
    previsoes = relatorio._processar_previsoes()

    # Verifica se as previsões foram agrupadas corretamente
    assert previsoes == {
        "2024-09-15": ["Chuva forte em várias regiões."],
        "2024-09-16": ["Néblina leve durante a manhã."]
    }


# Teste para garantir que o relatório em PDF é gerado
def test_gerar_relatorio_pdf(tmp_path, mocker):
    # Cria um arquivo bruto temporário
    caminho_bruto = tmp_path / "bruto.txt"
    caminho_bruto.write_text(
        "2024-09-15T12:00 Chuva forte em várias regiões.\n2024-09-16T08:00 Neblina leve durante a manhã.")

    # Instancia a classe
    relatorio = RelatorioMeteorologico(telefones=["01234567891"], data="2024-09-15T00:00", envia_email=False,
                                       caminho_bruto=caminho_bruto)

    # Mock para o PDF para não depender do arquivo físico
    mock_pdf = mocker.patch('fpdf.FPDF.output')

    # Gera o relatório
    caminho_pdf = relatorio.gerar_relatorio_pdf("Cliente Teste")

    # Verifica se o PDF foi gerado no local correto
    mock_pdf.assert_called_once()
    assert caminho_pdf == f"relatorio_Cliente Teste.pdf"


# Teste para verificar o envio de e-mail (com mock)
def test_enviar_email_com_anexo(mocker):
    # Instancia a classe sem precisar de conteúdo bruto
    relatorio = RelatorioMeteorologico(telefones=["01234567891"], data="2024-09-15T00:00", envia_email=False,
                                       caminho_bruto="bruto.txt")

    # Mock do envio de e-mail
    mock_smtp = mocker.patch('smtplib.SMTP')

    # Caminho fictício do PDF
    caminho_pdf = "/tmp/relatorio_Cliente Teste.pdf"

    # Envia o e-mail com o anexo
    relatorio.enviar_email_com_anexo(["destino@example.com"], caminho_pdf)

    # Verifica se o e-mail foi enviado
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    mock_smtp_instance.sendmail.assert_called_once()


# Teste para verificar se o arquivo bruto não existe
def test_arquivo_bruto_nao_existe():
    with pytest.raises(FileNotFoundError):
        RelatorioMeteorologico(telefones=["01234567891"], data="2024-09-15T00:00", envia_email=False,
                               caminho_bruto="arquivo_inexistente.txt")


# Teste para verificar logs
def test_logs(mocker, tmp_path, caplog):
    caminho_bruto = tmp_path / "bruto.txt"
    caminho_bruto.write_text("2024-09-15T12:00 Chuva forte em várias regiões.\n")

    # Capta os logs e garante que o arquivo foi carregado
    with caplog.at_level(logging.INFO):
        RelatorioMeteorologico(telefones=["01234567891"], data="2024-09-15T00:00", envia_email=False,
                               caminho_bruto=caminho_bruto)
        assert "Arquivo bruto carregado com sucesso." in caplog.text

