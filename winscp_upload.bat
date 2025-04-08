@echo off

rem host_address = sftp://backups-ftp:Conexaoba123@160.238.226.1:2230/
set host_address=%~1
set file_to_upload=%~2
set backup_folder_path=%~3

echo host_address: %host_address%
echo file_to_upload: %file_to_upload%
echo backup_folder_path: %backup_folder_path%

echo Verificando existência da pasta %backup_folder_path% no host %host_address%
"winscp\WinSCP.com" /ini=nul /log=log_winscp.log /command "open %host_address% -certificate="*"" "stat ""%backup_folder_path%""" "exit"

if %ERRORLEVEL% equ 0 (
  echo Pasta %backup_folder_path% já existe...
) else (
  echo Pasta %backup_folder_path% não existe, criando...
  "winscp\WinSCP.com" /ini=nul /log=log_winscp.log /command "open %host_address% -certificate="*"" "mkdir ""%backup_folder_path%""" "exit"
)

echo Enviando arquivo %file_to_upload% para %backup_folder_path%...
"winscp\WinSCP.com" /ini=nul /log=log_winscp.log /command "open %host_address% -certificate="*"" "put ""%file_to_upload%"" ""%backup_folder_path%""" "exit"

if %ERRORLEVEL% equ 0 (
  echo Script finalizado com sucesso!
  exit /b 0
) else (
  echo Script finalizado com erro!
  exit /b 1
)