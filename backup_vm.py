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

# Biblioteca para criar o arquivo zip do backup
import shutil

# Biblioteca para gerenciar argumentos na chamada do script
import argparse

# Biblioteca para gerenciar subprocessos (Janela do Powershell e do WinSCP) e capturar o retorno
import subprocess

# Biblioteca para interagir com o interpretador do Python
import sys

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

# Biblioteca para enviar requisições (Utilizando para comunicação com bot do telegram)
import requests

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
            print_and_log(f"""\n*********************************************************\n
                        Programa finalizado com sucesso!
                        \n/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/\n""")
            sys.exit(0)
        case 1:
            print_and_log(f"""\n*********************************************************\n
                        Programa finalizado com erro!
                        \n/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/\n""", "critical")
            sys.exit(1)


#########################################################
# Capturando argumentos passados na execução do script
#########################################################

# Configurando funcionamento da biblioteca
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    allow_abbrev=False,
    add_help=False,
    prog='Backup VMs',
    usage='python backup_vm.py --vm "NOME DA VM" [--zip]',
    description="O script realiza backup da VM informada e envia para o servidor SFTP que foi configurado no arquivo settings.cfg.",
    epilog=':)')

# Configurando argumentos que podem ser passados
parser.add_argument('--vm', required=True, metavar='"NOME DA VM"',
                    help='(Obrigatório) Nome da VM que deseja fazer backup.')
parser.add_argument('--zip', help='(Opcional) Caso queira compactar o backup em zip antes de enviar ao servidor SFTP.',
                    action='store_true')
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help='Mostra essa mensagem e finaliza o script.')

# Capturando argumentos passados
args = parser.parse_args()

vm_to_backup = args.vm
make_zip_from_backup = args.zip
# Iremos informar os argumentos passados ao usuário apenas após criar o arquivo de log (próximo bloco do script)
# Pois assim poderemos gravar no log as informações passadas

#########################################################
# Configurando os logs do script
#########################################################

print(f"""\n/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/\n\nIniciando arquivo de log...""")

# Diretório onde os logs serão armazenados
log_dir = "logs"
# Criando o diretório caso não exista
os.makedirs(log_dir, exist_ok=True)
# Criando uma string com horário e id unico para essa execução do script
unique_time_id = f"{datetime.now().strftime('%d-%m-%Y__%H-%M-%S')}__{uuid.uuid4().hex}"

# Criando um nome para o log (formato: log__data__horário__id.log)
log_filename = os.path.join(
    log_dir,
    f"log__{unique_time_id}.log")

# Configurando o logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s:\n%(message)s\n"
)

print_and_log(f"""Arquivo de log iniciado com sucesso!""")

# Informando os argumentos passados na chamada do script para o usuário
print_and_log(f"""\n*********************************************************\n
---> Argumentos passados para o script:
Nome da VM para realizar backup -> {args.vm}
Deve comprimir o backup em zip? -> {args.zip}""")

#########################################################
# Lendo e salvando os dados do arquivo settings.cgf:
# (O arquivo deve estar na mesma pasta do script.)
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
local_backups_base_folder_path = ""

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

# Lendo e validando o parâmetro script_settings -> local_backups_base_folder_path
try:
    local_backups_base_folder_path = config.get(
        'script_settings', 'local_backups_base_folder_path')
    if local_backups_base_folder_path.strip() == "":
        print_and_log(
            "\nErro: Parâmetro 'script_settings -> local_backups_base_folder_path' não pode estar vazio.", "critical")
        end_script(1)
except ValueError:
    print_and_log(
        "\nErro: Parâmetro 'script_settings -> local_backups_base_folder_path' precisa ser uma string.", "critical")
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

    # Lendo e validando o parâmetro ftp_info -> backups_base_folder_path
    try:
        ftp_info["backups_base_folder_path"] = config.get(
            'ftp_info', 'backups_base_folder_path')
        if ftp_info["backups_base_folder_path"].strip() == "":
            print_and_log(
                "\nErro: Parâmetro 'ftp_info -> backups_base_folder_path' não pode estar vazio.", "critical")
            end_script(1)
    except ValueError:
        print_and_log(
            "\nErro: Parâmetro 'ftp_info -> backups_base_folder_path' precisa ser uma string.", "critical")
        end_script(1)

print_and_log(f"""
Configurações:
---> Configurações de logs:
Número máximo de logs -> {max_logs}
---> Configurações do script:
Deve enviar backup para o SFTP? -> {upload_backup_to_ftp}
Deve limpar backup local? -> {clean_local_backup_after_upload}
Caminho local para o backup -> {local_backups_base_folder_path}
---> Configurações do servidor SFTP:
{"(Upload para o servidor desabilitado)" if not upload_backup_to_ftp else
 f"""Endereço -> {ftp_info['host']}
Porta -> {ftp_info['port']}
Usuário -> {ftp_info['user']}
Senha -> {ftp_info['pass']}
Caminho para salvar backup no SFTP -> {ftp_info['backups_base_folder_path']}"""}
""")


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
              Inciando backup da VM: {vm_to_backup}""")

# Armazenando o caminho em que o script está rodando
path = os.getcwd()
# Arazendando o modo de encoding do sistema em que o script está rodando
# (normalmente UTF-8, porém o UTF-8 dá erro no powershell,
# se o script rodar no windows vai retornar encoding: CodePage850,
# vai rodar com sucesso porém os acentos no log vão ficar bugados.)
encoding = os.device_encoding(1)
# Nome da pasta raiz onde será armazenado todos os backups
backup_script_name = "script_teste"
# Nome da pasta que será armazenado este backup da VM
backup_folder_name = f"{vm_to_backup}__{unique_time_id}"
# Armazenando o caminho completo do backup para usar depois
backup_folder_full_path = f"{local_backups_base_folder_path}{backup_folder_name}"

print_and_log(f"""Abrindo o script de backup no powershell...""")

p = subprocess.run(
    ["powershell.exe",
     "-NoProfile",
     "-ExecutionPolicy", "Bypass",
     "-File", f"{path}\\{backup_script_name}.ps1", f"{vm_to_backup}", f"{local_backups_base_folder_path}", f"{backup_folder_name}"],
    capture_output=True, text=True, encoding=encoding
)

if p.stderr:
    print_and_log("\nErro ao executar backup!", "critical")
    print_and_log(
        f"\nRetorno da execução do powershell:\n\n{p.stdout}", "critical")
    print_and_log(f"\nErro:\n{p.stderr}", "critical")
    end_script(1)
else:
    print_and_log("\nBackup concluído com sucesso!")
    print_and_log(
        f"\nRetorno da execução do powershell:\n\n{p.stdout}")


#########################################################
# Criar um arquivo zip do backup realizado
# (se informado nos argumentos ao chamar o script)
#########################################################

if make_zip_from_backup:
    backup_zip_name = f"{vm_to_backup}__{unique_time_id}"
    backup_zip_file_with_full_path = f"{local_backups_base_folder_path}{backup_zip_name}"
    print_and_log(f"""\n*********************************************************\n
                Compactando backup para o arquivo: {backup_zip_file_with_full_path}.zip""")
    try:
        shutil.make_archive(root_dir=backup_folder_full_path,
                            format='zip', base_name=backup_zip_file_with_full_path)
    except Exception as error:
        # Informa ao usuário
        print_and_log(
            f"Erro ao compactar backup para o arquivo {backup_zip_name}.zip!\nErro: {error}", "critical")
    else:
        print_and_log("Backup compactado com sucesso!")

#########################################################
# Conectar com o servidor FTP e fazer upload do backup realizado
# (caso habilitado nas configurações: "settings.cfg")
#########################################################

# Caso configurado para fazer upload do backup para o servidor SFTP
if upload_backup_to_ftp:
    print_and_log(f"""\n*********************************************************\n
                Realizando upload do backup da VM {vm_to_backup} para o servidor SFTP...""")
    print_and_log(
        f"\nServidor SFTP configurado: \nHost: {ftp_info['host']}\nPort: {ftp_info['port']}\nUser: {ftp_info['user']}\nPass: {ftp_info['pass']}\nBackups folder path: {ftp_info['backups_base_folder_path']}\n")

    # Arazendando o modo de encoding do sistema em que o script está rodando
    # (normalmente UTF-8, porém o UTF-8 dá erro no powershell,
    # se o script rodar no windows vai retornar encoding: CodePage850,
    # vai rodar com sucesso porém os acentos no log vão ficar bugados.)
    encoding = os.device_encoding(1)
    # Criando URL para conexão com o servidor SFTP
    host_address = f"sftp://{ftp_info['user']}:{ftp_info['pass']}@{ftp_info['host']}:{ftp_info['port']}/"
    # Caso informado para não compactar a pasta
    if not make_zip_from_backup:
        # Criando caminho da pasta usando barra invertida pq o Windows é assim...
        item_to_upload = f"{backup_folder_full_path}".replace("/", "\\")
    # Caso informado para compactar a pasta
    else:
        item_to_upload = f"{backup_zip_file_with_full_path}.zip".replace(
            "/", "\\")
    # Criando o caminho onde o backup será armazenado no servidor SFTP
    backup_folder_path = f"{ftp_info["backups_base_folder_path"]}{vm_to_backup}/"

    print_and_log(f"""Realizando upload do backup no script WinSCP...""")
    # Rodando o script BAT que irá enviar o backup para o servidor SFTP utilizando o WinSCP
    p = subprocess.Popen(f'''{path}\\winscp_upload.bat "{host_address}" "{item_to_upload}" "{backup_folder_path}" "{ftp_info["backups_base_folder_path"]}"''',
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding=encoding)
    # Capturando o retorno do script
    output, err = p.communicate()
    # Capturando o código de retorno do script
    exit_code = p.returncode

    # Caso o script BAT retorne com erro
    if exit_code != 0:
        # Informar ao usuário e finalizar o script
        print_and_log(
            "\nErro ao executar upload no script WinSCP!", "critical")
        print_and_log(
            f"\nRetorno da execução do upload no script WinSCP:\n\n{output}", "critical")
        print_and_log(f"\nErro:\n{err}", "critical")
        end_script(1)
    # Caso retorne com sucesso
    else:
        # Informar ao usuário
        print_and_log("\nUpload no script WinSCP concluído com sucesso!")
        print_and_log(
            f"\nRetorno da execução do upload no script WinSCP:\n\n{output}")
# Caso configurado para não fazer upload para o servidor SFTP
else:
    # Informa ao usuário
    print_and_log(f"""\n*********************************************************\n
                Script configurado para não fazer upload para o servidor SFTP...""")

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
                        print_and_log(f"Removendo arquivo: {file_path}")
                        os.unlink(file_path)
                    # Caso seja uma pasta
                    else:
                        # Chama a função novamente para verificar os itens dentro da subpasta
                        clear_folder(file_path)
                        # Após verificar e remover qualquer item dentro, remove a pasta
                        print_and_log(f"Removendo pasta: {file_path}")
                        os.rmdir(file_path)
                # Caso ocorra algum erro na remoção dos itens
                except Exception as error:
                    # Informa ao usuário
                    print_and_log(
                        f"Erro na remoção do item!\nErro: {error}", "critical")
                else:
                    print_and_log("Remoção concluída com sucesso!")

    # Chama a função para limpar a pasta do backup local
    print_and_log("Esvaziando a pasta do backup...")
    try:
        clear_folder(backup_folder_full_path)
    except Exception as error:
        # Informa ao usuário
        print_and_log(
            f"Erro ao esvaziar a pasta do backup!\nErro: {error}", "critical")
    else:
        print_and_log("Pasta do backup esvaziada com sucesso!")

    # Após esvaziar qualquer item dentro, remove a pasta
    print_and_log("Removendo a pasta do backup...")
    try:
        os.rmdir(backup_folder_full_path)
    except Exception as error:
        print_and_log(
            f"Erro ao remover a pasta do backup!\nErro: {error}", "critical")
    else:
        print_and_log("Pasta do backup removida com sucesso!")

    # Caso tenha sido criado um arquivo zip do backup
    if make_zip_from_backup:
        # Remove o arquivo zip do backup
        print_and_log("Removendo o arquivo zip do backup...")
        try:
            os.unlink(f"{backup_zip_file_with_full_path}.zip")
        except Exception as error:
            print_and_log(
                f"Erro ao remover o arquivo zip do backup!\nErro: {error}", "critical")
        else:
            print_and_log("Arquivo zip do backup removido com sucesso!")
# Caso configurado para não limpar o backup salvo localmente
else:
    # Informa ao usuário
    print_and_log(f"""\n*********************************************************\n
                Script configurado para não limpar o backup salvo localmente...""")

#########################################################
# Limpando o backup local
# (caso habilitado nas configurações: "settings.cfg")
#########################################################

telegram_bot_token = "7264342339:AAHkYJaFgkQNQmYcIVY2KX6zYN4FzNgLW5s"
telegram_group_chat_id = 6674522493
message = f"(TESTE)\n✅ SUCESSO: Backup da VM {vm_to_backup} realizado com sucesso!\n(*￣▽￣*)ブ"
url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

response = requests.post(
    url=url, data={'chat_id': telegram_group_chat_id, 'text': message})

# Throw an exception if Telegram API fails
response.raise_for_status()

print(response.json())

# --------------------------------------------------------
# Finalizando o programa
# --------------------------------------------------------

# Finaliza o script
end_script(0)
