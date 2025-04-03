# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# (Por padrão:)
# O script faz pipipipopopo

# Alterando o arquivo settings.cfg (na mesma pasta do executável), é possível:
# - Alterar os dados de conexão com o servidor FTP.
# - Definir um número máximo de logs guardados no sistema

# --------------------------------------------------------

# Passo a passo padrão do script:

# 1 - Aaaaaaaaaaaaaaaa
# 2 - Bbbbbbbbbbbb
# 3 - Cccccccccccccc

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

#########################################################
# Importando as bibliotecas utilizadas:
#########################################################

# Biblioteca para interagir com o servidor FTP
from ftplib import FTP

# Biblioteca para gerenciar subprocessos (Janela do Powershell) e capturar o retorno
import subprocess

# Biblioteca para interagir com o interpretador do Python
import sys

# Biblioteca para manipular JSON
import json

# Biblioteca para manipular data / horário
from datetime import datetime

# Biblioteca para gerenciar o arquivo de configurações (settings.cfg)
import configparser

# Biblioteca pra gerenciar os arquivos de log do script
import logging

# Biblioteca para utilizar funções do sistema operacional
import os

# Biblioteca para gerar um ID único para cada log
import uuid

# Biblioteca de busca de arquivos que batem com uma expressão
# (Um regex pra arquivos)
import glob

#########################################################
# Declarando função para imprimir mensagem na tela e salvar nos logs.
# (Para evitar redundância)
# A função recebe uma mensagem e um level de log (opcional).
# Padrão: "info"
# Valores possíveis: "info", "debug", "warning", "error", "critical".
#########################################################


def print_and_log(message, level="info"):
    # Removendo qualquer espaço em branco no início da mensagem
    message = '\n'.join([m.lstrip() for m in message.split('\n')])
    match level:
        case "info":
            print(message)
            logging.info(message.strip())
        case "debug":
            print(message)
            logging.debug(message.strip())
        case "warning":
            print(message)
            logging.warning(message.strip())
        case "error":
            print(message)
            logging.error(message.strip())
        case "critical":
            print(message)
            logging.critical(message.strip())
        case _:
            print(f"\nO level de log {level} não existe!")
            logging.critical(f"O level de log {level} não existe!")
            end_script(1)

#########################################################
# Declarando uma função simples para finalizar
# o script, mostrar uma mensagem e salvar no log
#########################################################


def end_script(finish_code: 0):
    match finish_code:
        case 0:
            print_and_log(f"""\n#########################################################\n
                        Programa finalizado com sucesso!
                        \n#########################################################\n""")
            sys.exit(0)
        case 1:
            print_and_log(f"""\n#########################################################\n
                        Programa finalizado com erro!
                        \n#########################################################\n""", "critical")
            sys.exit(1)

#########################################################
# Configurando os logs do script
#########################################################


print(f"""\n*********************************************************\n\nIniciando arquivo de log...""")

# Diretório onde os logs serão armazenados
log_dir = "logs"
# Criando o diretório caso não exista
os.makedirs(log_dir, exist_ok=True)

# Criando um nome para o log (formato: log__data__horário__id.log)
log_filename = os.path.join(
    log_dir,
    f"log__{datetime.now().strftime('%d-%m-%Y__%H-%M-%S')}__{uuid.uuid4().hex}.log")

# Configurando o logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s:\n%(message)s\n"
)

print_and_log(f"""Arquivo de log iniciado com sucesso!""")

#########################################################
# Lendo e salvando os dados do arquivo settings.cgf:
# (O arquivo deve estar na mesma pasta do script.)
# Modelo:
"""
#--------------------------------------------------------
# Settings #
#--------------------------------------------------------
# Configurações de funcionamento do script
[script_settings]
# Salvar os dados obtidos no banco de dados? (true / false)
save_on_db = false
# O programa deve verificar uma data personalizada? (true / false)
# (Caso falso, o programa verificará os dados de ontem)
custom_verify = false
# Caso verdadeiro, qual data deve ser verificada? (Dia/Mês/Ano - xx/xx/xxxx)
verify_date = 18/03/2025
#--------------------------------------------------------
# Configurações do funcionamento dos logs
[log_settings]
# Máximo de logs a serem guardados no sistema (integer)
max_logs = 5
#--------------------------------------------------------
# Dados para conexão com o banco PostgreSQL:
[db_info]
# Endereço do servidor: (string)
host = 127.0.0.1
# Usuário com acesso de leitura/escrita (string)
user = Shakya
# Senha do usuário (string)
password = shk
# Nome do banco a ser utilizado (string)
dbname = UNIFI
# Porta de acesso do servidor (integer)
port = 5432
# Nome da tabela que ficará salvo os dados (string)
table = diagnostics
#--------------------------------------------------------
"""
#########################################################

print_and_log(f"""\n*********************************************************\n
              Iniciando leitura das configurações...""")

# Inicializando o configparser
config = configparser.ConfigParser()

# Tentando abrir o arquivo settings.cfg
try:
    # Abrindo o aquivo
    with open('settings.cfg') as file:
        # Lendo o arquivo
        config.read_file(file)
# Caso encontre algum erro
except IOError as error:
    print_and_log(f"""\nErro ao tentar abrir o arquivo settings.cfg:\n
        {error}\n
        #########################################################\n""", "critical")
    end_script(1)

# Inicializando variáveis que serão lidas
ftp_info = {}
upload_backup_to_ftp = None
clean_local_backup_after_upload = None
max_logs = None

# Inicializando variáveis fixas (que não podem ser alteradas via "settings.cfg")
base_path = "C:/vm_backups"
vm_name = "ZABBIX_OLT"

# Lendo e validando o parâmetro log_settings -> max_logs
try:
    max_logs = config.getint('log_settings', 'max_logs')
except ValueError:
    print_and_log(
        "\nErro: Parâmetro 'log_settings -> max_logs' precisa ser um número inteiro.", "critical")
    end_script(1)

# Lendo e validando o parâmetro script_settings -> upload_backup_to_ftp
try:
    upload_backup_to_ftp = config.getboolean(
        'script_settings', 'upload_backup_to_ftp')
except ValueError:
    print_and_log(
        "\nErro: Parâmetro 'script_settings -> upload_backup_to_ftp' precisa ser um booleano.", "critical")
    end_script(1)

# Lendo e validando o parâmetro script_settings -> clean_local_backup_after_upload
try:
    clean_local_backup_after_upload = config.getboolean(
        'script_settings', 'clean_local_backup_after_upload')
except ValueError:
    print_and_log(
        "\nErro: Parâmetro 'script_settings -> clean_local_backup_after_upload' precisa ser um booleano.", "critical")
    end_script(1)

# Caso configurado para fazer upload do backup pro servidor FTP
if upload_backup_to_ftp is True:
    # Lendo e validando o parâmetro ftp_info -> host
    try:
        ftp_info["host"] = config.get('ftp_info', 'host')
        if ftp_info["host"].strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'ftp_info -> host' não pode estar vazio.", "critical")
            end_script(1)
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'ftp_info -> host' precisa ser uma string.", "critical")
        end_script(1)

    # Lendo e validando o parâmetro ftp_info -> port
    try:
        ftp_info["port"] = config.getint('ftp_info', 'port')
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'ftp_info -> port' precisa ser um número inteiro.", "critical")
        end_script(1)

    # Lendo e validando o parâmetro ftp_info -> user
    try:
        ftp_info["user"] = config.get('ftp_info', 'user')
        if ftp_info["user"].strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'ftp_info -> user' não pode estar vazio.", "critical")
            end_script(1)
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'ftp_info -> user' precisa ser uma string.", "critical")
        end_script(1)

    # Lendo e validando o parâmetro ftp_info -> pass
    try:
        ftp_info["pass"] = config.get('ftp_info', 'pass')
        if ftp_info["pass"].strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'ftp_info -> pass' não pode estar vazio.", "critical")
            end_script(1)
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'ftp_info -> pass' precisa ser uma string.", "critical")
        end_script(1)

'''
# Lendo e validando o parâmetro vms_to_backup -> vms_list
try:
    vms_to_backup = json.loads(config.get("vms_to_backup", "vms_list"))
    for vm_name in vms_to_backup:
        if vm_name.strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'vms_to_backup -> vms_list' não pode conter uma nome vazio.", "critical")
            end_script(1)
except ValueError:
    print_and_log(
        "\nErro: Parâmetro 'vms_to_backup -> vms_list' precisa ser uma lista de strings.", "critical")
    end_script(1)

print(vms_to_backup)
'''
'''
# Lendo e validando o parâmetro script_settings -> save_on_db
try:
    save_on_db = config.getboolean('script_settings', 'save_on_db')
except ValueError:
    print_and_log(
        "\nErro: Parâmetro 'script_settings -> save_on_db' precisa ser um booleano.", "critical")
    end_script(1)

# Lendo e validando o parâmetro script_settings -> custom_verify
try:
    custom_verify = config.getboolean('script_settings', 'custom_verify')
except ValueError:
    print_and_log(
        "\nErro: Parâmetro 'script_settings -> custom_verify' precisa ser um booleano.", "critical")
    end_script(1)

# Caso configurado para verificar uma data customizada
if custom_verify is True:
    # Lendo e validando o parâmetro script_settings -> verify_date
    try:
        verify_date = config.get('script_settings', 'verify_date')
        if verify_date.strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'script_settings -> verify_date' não pode estar vazio.", "critical")
            end_script(1)
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'script_settings -> verify_date' precisa ser uma string.", "critical")
        end_script(1)

# Caso configurado para salvar no banco de dados
if save_on_db is True:
    # Lendo e validando o parâmetro dbinfo -> host
    try:
        db_info["host"] = config.get('db_info', 'host')
        if db_info["host"].strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'dbinfo -> host' não pode estar vazio.", "critical")
            end_script(1)
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'dbinfo -> host' precisa ser uma string.", "critical")
        end_script(1)

    # Lendo e validando o parâmetro dbinfo -> user
    try:
        db_info["user"] = config.get('db_info', 'user')
        if db_info["user"].strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'dbinfo -> user' não pode estar vazio.", "critical")
            end_script(1)
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'dbinfo -> user' precisa ser uma string.", "critical")
        end_script(1)

    # Lendo e validando o parâmetro dbinfo -> password
    try:
        db_info["password"] = config.get('db_info', 'password')
        if db_info["password"].strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'dbinfo -> password' não pode estar vazio.", "critical")
            end_script(1)
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'dbinfo -> password' precisa ser uma string.", "critical")
        end_script(1)

    # Lendo e validando o parâmetro dbinfo -> dbname
    try:
        db_info["dbname"] = config.get('db_info', 'dbname')
        if db_info["dbname"].strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'dbinfo -> dbname' não pode estar vazio.", "critical")
            end_script(1)
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'dbinfo -> dbname' precisa ser uma string.", "critical")
        end_script(1)

    # Lendo e validando o parâmetro dbinfo -> port
    try:
        db_info["port"] = config.getint('db_info', 'port')
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'dbinfo -> port' precisa ser um número inteiro.", "critical")
        end_script(1)

    # Lendo e validando o parâmetro dbinfo -> table
    try:
        db_info["table"] = config.get('db_info', 'table')
        if db_info["table"].strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'dbinfo -> table' não pode estar vazio.", "critical")
            end_script(1)
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'dbinfo -> table' precisa ser uma string.", "critical")
        end_script(1)

print_and_log(f"""\nConfigurações:
              db_info = {db_info}
              save_on_db = {save_on_db}
              custom_verify = {custom_verify}
              verify_date = {verify_date}
              max_logs = {max_logs}\n""")
'''

print_and_log(f"""\nConfigurações:
              max_logs = {max_logs}\n""")

print_and_log(f"""Configurações lidas com sucesso!""")


#########################################################
# Limpando logs antigos caso excedido o número máximo de logs
#########################################################

print_and_log(f"""\n*********************************************************\n
              Iniciando limpeza dos logs antigos...""")

# Pegar todos os arquivos no diretório dos logs que começam
# com "log_" e terminam com ".log" e botar em ordem de tempo
logs = sorted(glob.glob(os.path.join(log_dir, "log_*.log")),
              key=os.path.getctime)

# Caso exceda o número máximo de logs
if len(logs) > max_logs:
    print_and_log(f"""Quantidade de logs excedida!""")
    # Pegar os logs excedentes
    logs_a_excluir = logs[:len(logs) - max_logs]
    # Iterar sobre cada log
    for log in logs_a_excluir:
        # Excluir o log
        os.remove(log)
        print_and_log(f"""Log removido: {log}""")

print_and_log(f"""Limpeza dos logs antigos finalizada com sucesso!""")

#########################################################
# Rodar script para fazer backup nas VMs
#########################################################

print_and_log(f"""\n*********************************************************\n
              Inciando backup da VM: {vm_name}""")

path = os.getcwd()
encoding = os.device_encoding(1)
backup_script_name = "script_teste"

print_and_log(f"""Abrindo o script de backup no powershell...""")

p = subprocess.run(
    ["powershell.exe",
     "-NoProfile",
     "-ExecutionPolicy", "Bypass",
     "-File", f"{path}\\{backup_script_name}.ps1", f"{vm_name}"],
    capture_output=True, text=True, encoding=encoding
)

if p.stderr:
    print_and_log("Erro ao executar backup!", "critical")
    print_and_log(
        f"Retorno da execução do powershell:\n{p.stdout}", "critical")
    print_and_log(f"Erro:\n{p.stderr}", "critical")
    end_script(1)
else:
    print_and_log("Backup concluído com sucesso!")
    print_and_log(
        f"Retorno da execução do powershell:\n{p.stdout}")

#########################################################
# Conectar com o servidor FTP e fazer upload do backup realizado
# (caso habilitado nas configurações: "settings.cfg")
#########################################################

# Caso configurado para fazer upload do backup para o servidor FTP
if upload_backup_to_ftp:
    print_and_log(f"""\n*********************************************************\n
                Realizando upload do backup da VM {vm_name} para o servidor FTP...""")

    # A função abaixo verifica cada pasta e arquivo do backup recursivamente
    # e os envia para o servidor FTP

    def upload_folder(ftp, local_folder, remote_folder):

        print_and_log(
            f"Criando diretório {local_folder} no FTP...")

        try:
            # Tenta criar, no servidor FTP, a pasta informada ao chamar a função
            # (Recursivamente irá criar a pasta raiz e todas as subpastas)
            ftp.mkd(remote_folder)
        # Caso já exista
        except Exception:
            # Informa ao usuário
            print_and_log(f"Diretório {local_folder} já existe!")

        # Entra na pasta criada no servidor FTP
        ftp.cwd(remote_folder)

        # Itera sobre cada item local (arquivos e pastas) do backup realizado
        for item in os.listdir(local_folder):
            # Armazena o caminho que está sendo verificado
            local_path = os.path.join(local_folder, item)
            # Caso o caminho seja uma pasta
            if os.path.isdir(local_path):
                # Chama recursivamente a função para verificar os itens dessa pasta
                upload_folder(ftp, local_path, item)
            # Caso não seja uma pasta
            else:
                print_and_log(
                    f"Realizando upload do arquivo {local_path} para o servidor FTP...")
                try:
                    # Tenta ler o arquivo em formato binário
                    with open(local_path, "rb") as file:
                        # Realiza o upload
                        ftp.storbinary(f"STOR {item}", file)
                        print_and_log(
                            f"Upload do arquivo {local_path} realizado com sucesso...")
                # Caso ocorra algum erro na leitura ou no upload do arquivo
                except Exception as error:
                    # Informa o erro ao usuário
                    print_and_log(
                        f"Erro ao realizar upload do arquivo {local_path} para o servidor FTP\nErro: {error}", "critical")
        # Retorna ao diretório anterior
        ftp.cwd("..")

    print_and_log(
        f"Conectando com o servidor FTP...\nHost: {ftp_info['host']}\nPort: {ftp_info['port']}\nUser: {ftp_info['user']}\nPass: {ftp_info['pass']}")
    try:
        # Tenta realizar a conexão com o servidor FTP
        ftp = FTP()
        ftp.connect(ftp_info["host"], ftp_info["port"])
        ftp.login(ftp_info["user"], ftp_info["pass"])
    # Caso ocorra algum erro
    except Exception as error:
        # Informa ao usuário
        print_and_log(
            f"Erro ao conectar com o servidor FTP!\nErro: {error}", "critical")
        end_script(1)

    # Armazena os diretórios:
    # Onde está salvo o backup localmente,
    # Onde será salvo no servidor FTP
    local_folder = f"{base_path}/{vm_name}_bkp"
    remote_folder = f"{base_path}/{vm_name}_bkp"

    # Chama a função responsável por fazer upload do backup
    upload_folder(ftp, local_folder, remote_folder)

    print_and_log(
        f"Encerrando conexão com o servidor FTP...")
    # Fecha a conexão com o servidor FTP
    ftp.quit()
# Caso configurado para não fazer upload do backup para o servidor FTP
else:
    # Informa ao usuário
    print_and_log(f"""\n*********************************************************\n
                Script configurado para não salvar o backup no servidor FTP...""")

#########################################################
# Limpando o backup local
# (caso habilitado nas configurações: "settings.cfg")
#########################################################

# Caso configurado para limpar o backup salvo localmente
if clean_local_backup_after_upload:
    print_and_log(f"""\n*********************************************************\n
                Limpando o backup realizado localmente...""")

    # Função para limpar recursivamente o diretório informado

    def clear_folder(dir):
        # Caso seja uma pasta
        if os.path.exists(dir):
            # Itera sobre cada item da pasta
            for file in os.listdir(dir):
                # Armazena o caminho que está sendo verificado
                file_path = os.path.join(dir, file)
                try:
                    # Caso seja um arquivo
                    if os.path.isfile(file_path):
                        # Apaga o arquivo
                        os.unlink(file_path)
                    # Caso seja uma pasta
                    else:
                        # Chama a função novamente para verificar os itens dentro da subpasta
                        clear_folder(file_path)
                        # Após verificar e remover qualquer item dentro, remove a pasta
                        os.rmdir(file_path)
                # Caso ocorra algum erro na remoção dos itens
                except Exception as error:
                    # Informa ao usuário
                    print_and_log(
                        f"Erro ao limpar o diretório de backup local!\nErro: {error}", "critical")

    # Chama a função para limpar o backup local
    clear_folder(base_path)
# Caso configurado para não limpar o backup salvo localmente
else:
    # Informa ao usuário
    print_and_log(f"""\n*********************************************************\n
                Script configurado para não limpar o backup salvo localmente...""")

# --------------------------------------------------------
# Finalizando o programa
# --------------------------------------------------------

# Finaliza o script
end_script(0)
