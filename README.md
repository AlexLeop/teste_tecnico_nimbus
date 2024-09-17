Aqui está o conteúdo sugerido para o arquivo `README.md` do seu projeto:

---

# Nimbus - Teste Técnico

Este repositório contém duas aplicações desenvolvidas para o teste técnico da Nimbus. As aplicações são responsáveis por processar dados meteorológicos recebidos via protocolo TCP/IP e gerar relatórios meteorológicos em PDF com base nos dados recebidos. Este README descreve como configurar, rodar e testar cada uma das aplicações.

## Estrutura do Projeto

```
Script/
    conexao/
        __init__.py
        tests/
            test_client.py
            test_server.py
        client.py
        server.py
    relatorios/
        __init__.py
        app.log
        dados.txt
        previsoes.txt
        relatorios.py
venv/
.env
requirements.txt
```

### Descrição dos Diretórios e Arquivos
- **conexao/**: Contém o código para a aplicação de recepção de dados (servidor e cliente).
  - **client.py**: Script que simula um cliente enviando dados ao servidor via TCP/IP.
  - **server.py**: Script do servidor que recebe, valida e armazena os dados recebidos.
  - **tests/**: Contém testes unitários para o cliente e servidor.
  
- **relatorios/**: Contém o código para a aplicação de geração de relatórios meteorológicos.
  - **app.log**: Arquivo de logs que registra os eventos da geração de relatórios.
  - **dados.txt**: Armazena as informações recebidas dos clientes (nome, email, telefone, idade).
  - **previsoes.txt**: Arquivo de previsões meteorológicas usadas na geração do relatório.
  - **relatorios.py**: Script para gerar o relatório meteorológico em PDF e, opcionalmente, enviar por e-mail.

- **venv/**: Ambiente virtual para a instalação dos pacotes Python necessários.
- **.env**: Arquivo de variáveis de ambiente (não incluído no repositório). Utilizado para armazenar credenciais de e-mail e outras informações sensíveis.
- **requirements.txt**: Arquivo com a lista de dependências do projeto para fácil instalação.

---

## Primeira Aplicação - Serviço de Recepção de Dados via TCP/IP

### Descrição

Esta aplicação atua como um serviço contínuo de recepção de dados via protocolo TCP/IP, utilizando a porta 5784. Os dados recebidos são validados e armazenados localmente. Um cliente envia os dados no formato `nome,email,telefone,idade` para o servidor.

### Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

### Configuração

1. **Instalar dependências:**
   Antes de rodar a aplicação, certifique-se de que as dependências estão instaladas. Ative o ambiente virtual e instale as bibliotecas:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   .\venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Executar o Servidor:**

   Para iniciar o servidor TCP/IP, rode o script `server.py`:

   ```bash
   python conexao/server.py
   ```

   O servidor começará a escutar a porta 5784 e estará pronto para receber dados.

3. **Executar o Cliente:**

   Para simular o envio de dados, execute o script `client.py` passando os dados como argumento:

   ```bash
   python conexao/client.py --data "João,joao@nimbus.com,01234567891,30"
   ```

   O cliente enviará os dados para o servidor, e o servidor responderá com "Ok" caso os dados estejam no formato correto. Se houver erro, o cliente receberá uma mensagem de erro.

4. **Logs:**

   Todas as operações do servidor serão registradas no arquivo `app.log` dentro do diretório `relatorios/`.

---

## Segunda Aplicação - Geração de Relatórios Meteorológicos

### Descrição

Este script gera relatórios meteorológicos em formato PDF com base em um arquivo bruto de previsões. O relatório pode ser enviado por e-mail, caso a flag `--envia_email` seja utilizada.

### Configuração

1. **Configurar Variáveis de Ambiente:**

   As credenciais de e-mail e informações SMTP são configuradas via arquivo `.env` ou diretamente no ambiente de execução. O arquivo `.env` deve conter as seguintes variáveis:

   ```
   EMAIL=seu_email@example.com
   SENHA_EMAIL=sua_senha
   SMTP_SERVER=smtp.seuprovedor.com
   SMTP_PORT=587
   ```

2. **Executar o Script de Geração de Relatórios:**

   Para gerar o relatório, rode o script `relatorios.py` passando os parâmetros necessários:

   ```bash
   python relatorios/relatorios.py --telefones "01234567891" --data "2024-01-01T00:00" --bruto "relatorios/previsoes.txt"
   ```

   Isso irá gerar o relatório em PDF e salvar no diretório atual. O nome do PDF será gerado dinamicamente com base no nome do cliente recuperado dos dados armazenados.

3. **Envio de E-mail:**

   Para enviar o relatório por e-mail, adicione a flag `--envia_email` ao comando:

   ```bash
   python relatorios/relatorios.py --telefones "01234567891" --data "2024-01-01T00:00" --bruto "relatorios/previsoes.txt" --envia_email
   ```

   O script enviará o relatório para o e-mail do cliente associado ao telefone informado.

4. **Visualização de Logs:**

   Todas as ações do script serão registradas no arquivo `app.log` dentro do diretório `relatorios/`. Caso haja algum erro no processo de envio de e-mail ou na geração do PDF, os detalhes estarão neste arquivo.

---

## Testes

1. **Testes Unitários:**

   O projeto contém testes unitários básicos para validar as funções do cliente e do servidor. Os testes estão localizados no diretório `tests/` dentro da pasta `conexao`.

   Para rodar os testes, execute:

   ```bash
   python -m unittest discover -s conexao/tests
   ```

---

## Dependências

Todas as dependências estão listadas no arquivo `requirements.txt`. Para instalar, utilize o seguinte comando:

```bash
pip install -r requirements.txt
```

---

## Considerações Finais

Este projeto implementa as funcionalidades de recepção de dados via TCP/IP e geração de relatórios meteorológicos em PDF, atendendo aos requisitos do teste técnico da Nimbus. Em caso de dúvidas ou problemas, consulte o arquivo de log (`app.log`) ou verifique se as variáveis de ambiente estão configuradas corretamente no `.env`.
