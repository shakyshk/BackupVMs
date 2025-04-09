# Capturando o nome da VM que iremos fazer o backup
$vm_to_backup = $args[0]
# Capturando o nome da pasta raiz que guarda todos os backups localmente
$base_path_for_backups = $args[1]
# Capturando o nome da pasta que guardará o backup que será realizado
$backup_folder_name = $args[2]

Write-Host "##############################################################"
Write-Host "Informações capturadas:"
Write-Host "VM que será realizado backup: " + $vm_to_backup
Write-Host "Caminho raiz dos backups: " + $base_path_for_backups
Write-Host "Pasta para o backup da VM: " + $backup_folder_name
Write-Host "--------------------------------------------------------------"
Write-Host "Iniciando script de backup..."
Write-Host "--------------------------------------------------------------"
# Capturando o ID e regra de segurança da conta do usuário atual
$myWindowsID = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$myWindowsPrincipal = new-object System.Security.Principal.WindowsPrincipal($myWindowsID)

# Capturando a regra de segurança do papel de administrador
$adminRole = [System.Security.Principal.WindowsBuiltInRole]::Administrator

# Verificando se estamos rodando como Administrador
if ($myWindowsPrincipal.IsInRole($adminRole)) {
    # Caso estiver rodando como Administrador, alterar o título da janela para identificar
    Write-Host "Script rodando como Administrador!";
    $Host.UI.RawUI.WindowTitle = $myInvocation.MyCommand.Definition + "(Elevated)"
    clear-host
}
else {
    # Caso não estiver rodando como administrador, iniciar novamente o script pedindo os privilégios necessários
    Write-Host "Elevando acesso do script para Administrador...";
    
    # Criando um novo objeto para iniciar o powershell
    $newProcess = new-object System.Diagnostics.ProcessStartInfo "PowerShell";
    
    # Especificando o caminho e nome do script atual como parâmetro 
    $newProcess.Arguments = $myInvocation.MyCommand.Definition;
    
    # Indicando que o processo deve ser elevado
    $newProcess.Verb = "runas";
    
    # Iniciando novo processo
    [System.Diagnostics.Process]::Start($newProcess).WaitForExit();
}

# A partir daqui, estamos rodando como administrador:

# Se a pasta raiz dos backups não existir
Write-Host "--------------------------------------------------------------"
Write-Host "Verificando existência da pasta raiz dos backups..."
If (!(test-path -PathType container $base_path_for_backups)) {
    # Criar a pasta
    Write-Host "Pasta não existe, criando..."
    New-Item -ItemType Directory -Path $base_path_for_backups | Out-Null
}
else {
    Write-Host "Pasta já existe..."
}
Write-Host "--------------------------------------------------------------"
# Criando o caminho onde será armazenado o backup dessa VM
$path_for_backup = Join-Path $base_path_for_backups $backup_folder_name
# Se a pasta de backup dessa VM não existir
Write-Host "Verificando existência da pasta que guardará o backup..."
If (!(test-path -PathType container $path_for_backup)) {
    # Criar a pasta
    Write-Host "Pasta não existe, criando..."
    New-Item -ItemType Directory -Path $path_for_backup | Out-Null
}
else {
    Write-Host "Pasta já existe..."
}
Write-Host "--------------------------------------------------------------"
Write-Host "Iniciando backup..."

# Realizando o backup da VM
#Export-VM -Name $vm_to_backup -Path $path_for_backup

Write-Host "Backup finalizado!"
Write-Host "##############################################################"
