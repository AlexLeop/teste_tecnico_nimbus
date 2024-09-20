import json
from fpdf import FPDF
from datetime import datetime
from dateutil import parser as date_parser
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Configuração de logs
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')


class RelatorioMeteorologico:
    """
    Classe responsável pela geração de relatórios meteorológicos em PDF, com envio opcional por e-mail.
    O relatório contém seções de análise e previsão meteorológica, com agrupamento de fenômenos e realce
    de eventos importantes.
    """

    def __init__(self, telefones, data, envia_email, caminho_bruto):
        """
        Inicializa a classe com os parâmetros fornecidos.

        Parâmetros:
        telefones (list): Lista de telefones dos destinatários.
        data (str): Data de confecção do relatório no formato ISO.
        envia_email (bool): Flag indicando se o relatório deve ser enviado por e-mail.
        caminho_bruto (str): Caminho para o arquivo bruto de previsões meteorológicas.
        """
        self.telefones = telefones
        self.data = date_parser.parse(data)
        self.envia_email = envia_email
        self.caminho_bruto = caminho_bruto
        self.conteudo_bruto = self._carregar_bruto()

    def _carregar_bruto(self):
        """
        Carrega o arquivo JSON bruto que contém as análises e previsões meteorológicas.

        Retorna:
        dict: Conteúdo do arquivo JSON carregado.

        Lança:
        FileNotFoundError: Caso o arquivo não seja encontrado.
        """
        try:
            with open(self.caminho_bruto, 'r', encoding='utf-8') as f:
                conteudo = json.load(f)
            logging.info("Arquivo bruto carregado com sucesso.")
            return conteudo
        except FileNotFoundError:
            logging.error("Arquivo bruto {} não encontrado.".format(self.caminho_bruto))
            raise

    # Métodos de estilização
    def set_fonte_negrito(self, pdf, tamanho=12):
        """
        Define a fonte para negrito com o tamanho especificado.

        Parâmetros:
        pdf (FPDF): Instância do FPDF para estilização.
        tamanho (int): Tamanho da fonte. Default é 12.
        """
        pdf.set_font('Arial', 'B', tamanho)

    def set_fonte_normal(self, pdf, tamanho=12):
        """
        Define a fonte para o texto normal com o tamanho especificado.

        Parâmetros:
        pdf (FPDF): Instância do FPDF para estilização.
        tamanho (int): Tamanho da fonte. Default é 12.
        """
        pdf.set_font('Arial', '', tamanho)

    def set_cor_fundo_vermelho(self, pdf):
        """
        Define o fundo vermelho para elementos de destaque.
        """
        pdf.set_fill_color(255, 0, 0)  # Vermelho

    def set_cor_fundo_cinza(self, pdf):
        """
        Define o fundo cinza escuro para elementos comuns.
        """
        pdf.set_fill_color(85, 85, 85)  # Cinza escuro

    def set_cor_texto_branco(self, pdf):
        """
        Define o texto branco.
        """
        pdf.set_text_color(255, 255, 255)  # Branco

    def set_cor_texto_preto(self, pdf):
        """
        Define o texto preto.
        """
        pdf.set_text_color(0, 0, 0)  # Preto

    def set_alinhamento_direita(self, pdf):
        """
        Define o alinhamento do texto à direita.
        """
        pdf.cell(200, 10, ln=True, align='R')

    def carregar_dados_clientes(self):
        """
        Carrega as informações do cliente salvas localmente no arquivo 'clientes.txt'.

        :return:
        - list: Lista com os dados do cliente.
        """
        with open('clientes.txt', 'r', encoding='utf-8') as f:
            clientes = [linha.strip().split(',') for linha in f.readlines()]
            return clientes

    # Funções principais de geração de relatório
    def gerar_relatorio_pdf(self):
        """
        Gera o relatório meteorológico em PDF, separando análises e previsões.

        O relatório é estruturado em duas seções:
        - Análises: Primeira seção do relatório.
        - Previsões: Segunda seção do relatório, com realce de eventos "fortes".

        Retorna:
        str: Caminho do PDF gerado.
        """
        clientes = self.carregar_dados_clientes()
        for cliente in clientes:
            nome_cliente = cliente[0]
            email_cliente = cliente[1]

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)

            # Adiciona a primeira página e a seção de Análise
            pdf.add_page()
            self._adicionar_cabecalho(pdf, nome_cliente)
            self._adicionar_secao_analise(pdf, "Análise")

            # Adiciona uma nova página e a seção de Previsão
            pdf.add_page()
            self._adicionar_cabecalho(pdf, nome_cliente)
            self._adicionar_secao_previsao(pdf, "Previsão")

            # Salva o PDF
            caminho_pdf = "relatorio_{}.pdf".format(nome_cliente)
            pdf.output(caminho_pdf)
            logging.info("Relatório PDF gerado: {}".format(caminho_pdf))
            return caminho_pdf

    def _adicionar_cabecalho(self, pdf, cliente_nome):
        """
        Adiciona o cabeçalho em todas as páginas do PDF.

        Parâmetros:
        pdf (FPDF): Objeto FPDF para manipulação do PDF.
        cliente_nome (str): Nome do cliente para exibição no cabeçalho.
        """
        # Adicionar a faixa azul marinho
        pdf.set_y(0)  # Começar no topo da página
        pdf.set_fill_color(5, 55, 95)  # Azul marinho
        pdf.rect(0, 0, pdf.w, 15, 'F')  # Desenhar o retângulo azul marinho

        # Adicionar o título centralizado
        pdf.set_font('Arial', 'B', 19)
        pdf.set_text_color(255, 255, 255)  # Branco para o texto
        pdf.cell(0, 15, 'Relatório Meteorológico', ln=True, align='C')

        # Adicionar a faixa amarela
        pdf.set_fill_color(255, 170, 60)
        pdf.rect(0, 15, pdf.w, 2, 'F')  # Desenhar o retângulo amarelo

        # Adicionar o cliente e a data de confecção na mesma linha
        pdf.set_y(12)  # Ajustar a posição Y para o conteúdo
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(0, 0, 0)  # Preto para o texto

        # Calcular a largura da página disponível para o conteúdo
        largura_pagina = pdf.w - 2 * pdf.l_margin

        # Calcular a largura das células
        largura_cliente = pdf.get_string_width('Cliente: {}'.format(cliente_nome))
        largura_data = pdf.get_string_width(
            'Data de Confecção: {}'.format(datetime.strftime(self.data, "%d/%m/%Y %H:%M")))

        # Adicionar a célula do cliente alinhada à esquerda
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(largura_cliente, 17, 'Cliente:', ln=False, align='L')
        pdf.set_font('Arial', '', 14)
        pdf.cell(largura_cliente, 17, '{}'.format(cliente_nome.capitalize()), ln=False, align='L')

        # Adicionar a célula da data alinhada à direita
        pdf.set_x(largura_pagina - (largura_data + 20))

        pdf.set_font('Arial', 'B', 14)
        pdf.cell(largura_data, 17, 'Data de Confecção:', ln=False, align='R')

        pdf.set_font('Arial', '', 14)
        pdf.cell(0, 17, ' {}'.format(datetime.strftime(self.data, "%d/%m/%Y")), ln=True, align='R')

        pdf.ln(10)  # Espaçamento após o cabeçalho

    def _adicionar_secao_analise(self, pdf, tipo_conteudo):
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(200, 10, '{}'.format(tipo_conteudo), ln=True)

        for item in self.conteudo_bruto['análise']:
            pdf.ln(2)
            fenomeno = item.get('fenomeno', 'Não especificado')
            mensagem = item.get('mensagem', 'Mensagem não disponível')

            # Verifica e aplica fundo vermelho se a mensagem contiver a palavra "forte"
            if "forte" in mensagem.lower():
                self.set_fonte_negrito(pdf)
                self.set_cor_texto_branco(pdf)
                self.set_cor_fundo_vermelho(pdf)
            else:
                self.set_fonte_negrito(pdf)
                self.set_cor_texto_branco(pdf)
                self.set_cor_fundo_cinza(pdf)

            pdf.cell(80, 8, fenomeno.capitalize(), ln=True, fill=True)
            pdf.ln(2)

            # Adicionar data e mensagem
            data_formatada_analise = datetime.strptime(item.get('data', '1970-01-01T00:00'), '%Y-%m-%dT%H:%M').strftime(
                '%d/%m/%Y as %H:%M ')
            largura_data = pdf.get_string_width(data_formatada_analise)

            self.set_fonte_negrito(pdf)  # Data em negrito
            self.set_cor_texto_preto(pdf)  # Texto preto
            pdf.cell(largura_data, 5, "{} ".format(data_formatada_analise), align='J', ln=False)

            self.set_fonte_normal(pdf)  # Mensagem normal

            # Exibe a mensagem na mesma linha ou com quebras
            largura_restante = pdf.w - 2.7 * (pdf.l_margin + largura_data)
            primeira_linha = pdf.get_string_width(mensagem)

            if primeira_linha < largura_restante:
                pdf.cell(0, 5, mensagem)
            else:
                parte_inicial = mensagem[:int(largura_restante)]
                pdf.cell(largura_restante, 5, parte_inicial, ln=True, align='J')
                restante_mensagem = mensagem[int(largura_restante):]
                pdf.multi_cell(0, 5, restante_mensagem)

            pdf.ln(5)

    def _adicionar_secao_previsao(self, pdf, tipo_conteudo):
        """
        Adiciona a seção de previsões ao PDF, agrupando previsões por fenômeno.

        A seção de previsão contém eventos meteorológicos esperados, e as previsões
        de fenômenos iguais (como chuva) são agrupadas por data e mensagem.

        Parâmetros:
        pdf (FPDF): Objeto FPDF para manipulação do PDF.
        """

        self.set_fonte_negrito(pdf, 16)
        pdf.cell(200, 10, '{}'.format(tipo_conteudo), ln=True, align='L')

        previsoes_agrupadas = self._agrupar_previsoes_por_fenomeno()

        for fenomeno, previsoes in previsoes_agrupadas.items():
            # Configura a cor e o estilo de acordo com o conteúdo
            self.set_fonte_negrito(pdf, 12)
            self.set_cor_texto_branco(pdf)

            # Exibir o fenômeno (com fundo vermelho se "forte" estiver em qualquer mensagem)
            if any("forte" in previsao['mensagem'].lower() for previsao in previsoes):
                self.set_cor_fundo_vermelho(pdf)
            else:
                self.set_cor_fundo_cinza(pdf)

            pdf.cell(80, 8, "{}".format(fenomeno.capitalize()), ln=True, fill=True)
            pdf.ln(2)

            # Agrupa as previsões por data e mensagem
            for previsao in previsoes:
                data_formatada = datetime.strptime(previsao['data'], '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y as %H:%M ')
                mensagem = previsao['mensagem']

                # Exibe a data em negrito
                largura_data = pdf.get_string_width(data_formatada)
                self.set_fonte_negrito(pdf)
                self.set_cor_texto_preto(pdf)
                pdf.cell(largura_data, 5, "{} ".format(data_formatada), ln=False)

                # Exibe a mensagem com quebra automática
                self.set_fonte_normal(pdf)
                largura_restante = pdf.w - 2.7 * (pdf.l_margin + largura_data)
                primeira_linha = pdf.get_string_width(mensagem)

                if primeira_linha < largura_restante:
                    pdf.cell(0, 5, mensagem)
                    pdf.ln(5)
                else:
                    parte_inicial = mensagem[:int(largura_restante)]
                    pdf.cell(largura_restante, 5, parte_inicial, ln=True, align='J')
                    restante_mensagem = mensagem[int(largura_restante):]
                    pdf.multi_cell(0, 5, restante_mensagem)
                    pdf.ln(5)
            pdf.ln(5)

    def _agrupar_previsoes_por_fenomeno(self):
        """
        Agrupa previsões por fenômeno, combinando datas e mensagens.

        :return:
        - dict: Dicionário com o fenômeno como chave e as previsões (data e mensagem) como valor.
        """
        previsoes_agrupadas = {}

        for previsao in self.conteudo_bruto['previsao']:
            fenomeno = previsao['fenomeno']

            if fenomeno not in previsoes_agrupadas:
                previsoes_agrupadas[fenomeno] = []

            previsoes_agrupadas[fenomeno].append({
                'data': previsao['data'],
                'mensagem': previsao['mensagem']
            })

        return previsoes_agrupadas

    def enviar_email_com_anexo(self, destinatarios, caminho_pdf):
        """
        Envia um e-mail com o PDF gerado como anexo.

        Parâmetros:
        destinatarios (list): Lista de e-mails dos destinatários.
        caminho_pdf (str): Caminho para o arquivo PDF gerado.
        """
        try:
            # Configurando a mensagem
            msg = MIMEMultipart()
            msg['From'] = os.getenv('EMAIL')
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = "Relatório Meteorológico - {}".format(self.data.strftime('%Y-%m-%d'))

            # Corpo do e-mail
            corpo = "Segue em anexo o relatório meteorológico solicitado."
            msg.attach(MIMEText(corpo))

            # Anexo PDF
            with open(caminho_pdf, "rb") as f:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(f.read())
                encoders.encode_base64(parte)
                parte.add_header('Content-Disposition',
                                 'attachment; filename={}'.format(os.path.basename(caminho_pdf)))
                msg.attach(parte)

            # Configuração do servidor SMTP
            server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')))
            server.starttls()
            server.login(os.getenv('EMAIL'), os.getenv('SENHA_EMAIL'))
            texto = msg.as_string()
            server.sendmail(os.getenv('EMAIL'), destinatarios, texto)
            server.quit()

            logging.info("Relatório enviado para: {}".format(', '.join(destinatarios)))
        except Exception as e:
            logging.error("Erro ao enviar e-mail para {}: {}".format(', '.join(destinatarios), e))
            raise


def main():
    # Argumentos de linha de comando
    import argparse
    parser = argparse.ArgumentParser(description='Script de geração de relatórios meteorológicos.')
    parser.add_argument('--telefones', required=True, help='Lista de telefones ou e-mails separados por vírgula')
    parser.add_argument('--data', required=True, help='Data no formato 2024-01-01T00:00')
    parser.add_argument('--envia_email', action='store_true', help='Flag para enviar e-mail')
    parser.add_argument('--bruto', required=True, help='Caminho para o arquivo bruto de previsões')
    args = parser.parse_args()

    # Cria instância da classe RelatorioMeteorologico
    relatorio = RelatorioMeteorologico(
        telefones=args.telefones.split(','),
        data=args.data,
        envia_email=args.envia_email,
        caminho_bruto=args.bruto
    )

    # Gerar o relatório PDF
    caminho_pdf = relatorio.gerar_relatorio_pdf()

    # Se a flag --envia_email for passada, envia o PDF por e-mail
    if args.envia_email:
        relatorio.enviar_email_com_anexo(relatorio.telefones, caminho_pdf)

    logging.info("Script concluído com sucesso.")


if __name__ == "__main__":
    main()
