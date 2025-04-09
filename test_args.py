import argparse

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    allow_abbrev=False,
    add_help=False,
    prog='Backup VMs',
    usage='python backup_vm.py --vm "NOME DA VM" [--zip]',
    description="O script realiza backup da VM informada e envia para o servidor SFTP que foi configurado no arquivo settings.cfg.",
    epilog=':)')

parser.add_argument('--vm', required=True, metavar='"NOME DA VM"',
                    help='(Obrigatório) Nome da VM que deseja fazer backup.')
parser.add_argument('--zip', help='(Opcional) Caso queira compactar o backup em zip antes de enviar ao servidor SFTP.',
                    action='store_true')
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help='Mostra essa mensagem e finaliza o script.')

args = parser.parse_args()

print(f"""---> Argumentos passados para o script:
Nome da VM para realizar backup -> {args.vm}
Deve comprimir o backup em zip? -> {args.zip}""")
