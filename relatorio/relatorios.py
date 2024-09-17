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
            logging.error(f"Arquivo bruto {self.caminho_bruto} não encontrado.")
            raise

    def gerar_relatorio_pdf(self):
        """
        Gera o relatório meteorológico em PDF, separando análises e previsões.

        O relatório é estruturado em duas seções:
        - Análises: Primeira seção do relatório.
        - Previsões: Segunda seção do relatório, com realce de eventos "fortes".

        Retorna:
        str: Caminho do PDF gerado.
        """
        cliente_nome = "Cliente XYZ"
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Adiciona a primeira página e a seção de Análise
        pdf.add_page()
        self._adicionar_cabecalho(pdf, cliente_nome, )
        self._adicionar_secao_analise(pdf, "Análise")

        # Adiciona uma nova página e a seção de Previsão
        pdf.add_page()
        self._adicionar_cabecalho(pdf, cliente_nome, )
        self._adicionar_secao_previsao(pdf, "Previsão")

        # Salva o PDF
        caminho_pdf = f"relatorio_{cliente_nome}.pdf"
        pdf.output(caminho_pdf)
        logging.info(f"Relatório PDF gerado: {caminho_pdf}")
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
        pdf.set_fill_color(18, 10, 143)  # Azul marinho
        pdf.rect(0, 0, pdf.w, 10, 'F')  # Desenhar o retângulo azul marinho

        # Adicionar o título centralizado
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(255, 255, 255)  # Branco para o texto
        pdf.cell(0, 10, 'Relatório Meteorológico', ln=True, align='C')

        # Adicionar a faixa amarela
        pdf.set_fill_color(255, 255, 0)
        pdf.rect(0, 10, pdf.w, 2, 'F')  # Desenhar o retângulo amarelo

        # Adicionar o cliente e a data de confecção na mesma linha
        pdf.set_y(12)  # Ajustar a posição Y para o conteúdo
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(0, 0, 0)  # Preto para o texto

        # Calcular a largura da página disponível para o conteúdo
        largura_pagina = pdf.w - 2 * pdf.l_margin

        # Calcular a largura das células
        largura_cliente = pdf.get_string_width(f'Cliente: {cliente_nome}')
        largura_data = pdf.get_string_width(f'Data de Confecção: {datetime.strftime(self.data, "%d-%m-%Y %H:%M")}')

        # Adicionar a célula do cliente alinhada à esquerda
        pdf.cell(largura_cliente, 10, f'Cliente: {cliente_nome}', ln=False, align='L')

        # Adicionar a célula da data alinhada à direita
        pdf.set_x(largura_pagina - largura_data)
        pdf.cell(largura_data, 10, f'Data de Confecção: {datetime.strftime(self.data, "%d-%m-%Y %H:%M")}', ln=True,
                 align='R')

        pdf.ln(4)  # Espaçamento após o cabeçalho

    def _adicionar_secao_analise(self, pdf, tipo_conteudo):
        """
        Adiciona a seção de análises ao PDF.

        A seção de análise contém eventos observados e registrados anteriormente.
        Cada análise inclui o fenômeno, a data e uma mensagem descritiva.

        Parâmetros:
        pdf (FPDF): Objeto FPDF para manipulação do PDF.
        tipo_conteudo (str): Tipo de conteúdo ("Análise" ou "Previsão").
        """
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(200, 10, f'{tipo_conteudo}', ln=True)

        for item in self.conteudo_bruto['análise']:
            pdf.ln(10)

            fenomeno = item.get('fenomeno', 'Não especificado')

            # Configurar o fundo colorido para o fenômeno
            if any(palavra in fenomeno.lower() for palavra in ['inundação']):
                pdf.set_font('Arial', 'B', 12)
                pdf.set_text_color(255, 255, 255)  # Branco para o texto
                pdf.set_fill_color(255, 0, 0)  # Cor vermelha para o fundo
                pdf.cell(80, 10, fenomeno, ln=True, fill=True)
                pdf.ln(2)  # Espaçamento após o fundo colorido

            else:
                pdf.set_font('Arial', 'B', 12)
                pdf.set_text_color(255, 255, 255)  # Branco para o texto
                pdf.set_fill_color(46, 46, 46)  # Cinza escuro para o fundo
                pdf.cell(80, 10, fenomeno, ln=True, fill=True)
                pdf.ln(2)  # Espaçamento após o fundo colorido

            # Formatação da data
            data_formatada_analise = (
                datetime.strptime(item.get('data', '1970-01-01T00:00'), '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y as %H:%M')
            )

            pdf.set_font('Arial', 'B', 12)  # Data em negrito
            pdf.set_text_color(0, 0, 0)  # Preto para o texto
            pdf.multi_cell(0, 10, f"{data_formatada_analise} ", align='L')  # Adicionar data

            pdf.set_font('Arial', '', 12)  # Mensagem normal
            pdf.multi_cell(0, 10, item.get('mensagem', 'Mensagem não disponível'), align='L')  # Adicionar mensagem

            pdf.ln(5)  # Espaçamento após a mensagem

    def _adicionar_secao_previsao(self, pdf, tipo_conteudo):
        """
        Adiciona a seção de previsões ao PDF, agrupando previsões por fenômeno.

        A seção de previsão contém eventos meteorológicos esperados. Eventos críticos
        com a palavra "forte" são destacados em vermelho para chamar a atenção.

        Parâmetros:
        pdf (FPDF): Objeto FPDF para manipulação do PDF.
        """

        # pdf.add_page()  # Adiciona a primeira página para a seção de previsões
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(200, 10, f'{tipo_conteudo}', ln=True, align='L')
        pdf.ln(2)  # Adiciona um espaço após o título

        previsoes_agrupadas = self._agrupar_previsoes()

        for data, eventos in previsoes_agrupadas.items():
            # Formatação da data
            data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y as %H:%M')

            for evento in eventos:
                # Adiciona título da previsão (data) se necessário
                pdf.set_font('Arial', 'B', 12)
                pdf.set_text_color(0, 0, 0)  # Preto para o texto
                pdf.ln(5)

                # Configuração de cor para o fenômeno
                if any(palavra in evento['fenomeno'].lower() for palavra in ['eventos', 'chuva', 'vento']):
                    pdf.set_font('Arial', 'B', 12)
                    pdf.set_text_color(255, 255, 255)  # Branco para o texto
                    pdf.set_fill_color(255, 0, 0)  # Cor vermelha para o fundo
                    pdf.cell(80, 10, f"{evento['fenomeno']}", ln=True, fill=True)
                    pdf.set_text_color(0, 0, 0)  # Preto para o texto
                    pdf.multi_cell(200, 10, f"{data_formatada}")
                else:
                    pdf.set_font('Arial', 'B', 12)
                    pdf.set_fill_color(46, 46, 46)  # Cinza para o marca-texto
                    pdf.set_text_color(255, 255, 255)  # Branco para o texto
                    pdf.cell(80, 8, f"{evento['fenomeno']}", ln=True, fill=True)
                    pdf.set_text_color(0, 0, 0)  # Preto para o texto
                    pdf.multi_cell(200, 10, f"{data_formatada}")

                pdf.set_text_color(0, 0, 0)  # Preto para o texto
                pdf.set_font('Arial', '', 12)
                mensagem = evento['mensagem']
                pdf.multi_cell(0, 10, f"{mensagem}", align='L')
                pdf.ln(5)

        # Adiciona uma nova página após adicionar todas as previsões, se necessário
        # pdf.add_page()  # Descomente se desejar adicionar uma nova página após todas as previsões

    def _agrupar_previsoes(self):
        """
        Agrupa previsões por data e fenômeno.

        Retorna:
        dict: Dicionário com previsões agrupadas por data.
        """
        previsoes_agrupadas = {}
        for item in self.conteudo_bruto['previsao']:
            data = item['data']
            if data not in previsoes_agrupadas:
                previsoes_agrupadas[data] = []
            previsoes_agrupadas[data].append(item)
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
            logging.error("Erro ao enviar e-mail: {}".format(e))
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
