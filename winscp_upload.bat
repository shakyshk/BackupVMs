@echo off

rem Capturando endereço do servidor FTP
set host_address=%~1
rem Capturando nome do item que desejamos enviar ao servidor FTP (pasta ou arquivo)
set file_to_upload=%~2
rem Capturando o caminho de onde será guardado o item no servidor FTP
set backup_folder_path=%~3
rem Capturando o caminho base de onde são guardados os backups no servidor FTP
set backups_base_folder_path=%~4
rem Capturando o caminho e nome do arquivo onde será armazenado o log do WinSCP
set path_log_winscp=%~5

echo ##############################################################
rem Mostranndo as informações capturadas ao usuário
echo Informações capturadas:
echo Endereço do servidor FTP: %host_address%
echo Item que será feito upload: %file_to_upload%
echo Caminho do arquivo no servidor FTP: %backup_folder_path%
echo Caminho base dos backups no servidor FTP: %backups_base_folder_path%
echo Onde será armazenado o LOG do WinSCP: %path_log_winscp%

echo --------------------------------------------------------------
echo Verificando a existência da pasta %backups_base_folder_path% no host %host_address%
echo --------------------------------------------------------------
echo Comunicando com o servidor FTP:
rem Verificando a existência da pasta raiz informado no servidor FTP
"winscp\WinSCP.com" /ini=nul /log=""%path_log_winscp%"" /command="option batch abort" "open %host_address% -explicittls -certificate="*"" "stat ""%backups_base_folder_path%""" "exit"
echo Comunicação finalizada!
echo --------------------------------------------------------------
rem Caso a pasta já exista
if %ERRORLEVEL% equ 0 (
  rem Informa ao usuário
  echo Pasta %backups_base_folder_path% já existe...
rem Caso a pasta não exista
) else (
  echo Pasta %backups_base_folder_path% não existe, criando...
  echo --------------------------------------------------------------
  echo Comunicando com o servidor FTP:
  rem Cria a pasta que irá guardar todos os backups no servidor FTP
  "winscp\WinSCP.com" /ini=nul /log=""%path_log_winscp%"" /command="option batch abort" "open %host_address% -explicittls -certificate="*"" "mkdir ""%backups_base_folder_path%""" "exit"
  echo Comunicação finalizada!
  echo --------------------------------------------------------------
  rem Caso a criação da pasta ocorra sem nenhuma falha
  if %ERRORLEVEL% equ 0 (
    rem Informa ao usuário
    echo Pasta %backups_base_folder_path% criada com sucesso!
  rem Caso ocorra alguma falha na criação da pasta
  ) else (
    rem Informa ao usuário
    echo Erro ao criar a pasta %backups_base_folder_path%!
  )
)

echo --------------------------------------------------------------
echo Verificando a existência da pasta %backup_folder_path% no host %host_address%
echo --------------------------------------------------------------
echo Comunicando com o servidor FTP:
rem Verificando a existência da pasta informada no servidor FTP
"winscp\WinSCP.com" /ini=nul /log=""%path_log_winscp%"" /command="option batch abort" "open %host_address% -explicittls -certificate="*"" "stat ""%backup_folder_path%""" "exit"
echo Comunicação finalizada!
echo --------------------------------------------------------------
rem Caso a pasta já exista
if %ERRORLEVEL% equ 0 (
  rem Informa ao usuário
  echo Pasta %backup_folder_path% já existe...
rem Caso a pasta não exista
) else (
  echo Pasta %backup_folder_path% não existe, criando...
  echo --------------------------------------------------------------
  echo Comunicando com o servidor FTP:
  rem Cria a pasta que irá guardar o item no servidor FTP
  "winscp\WinSCP.com" /ini=nul /log=""%path_log_winscp%"" /command="option batch abort" "open %host_address% -explicittls -certificate="*"" "mkdir ""%backup_folder_path%""" "exit"
  echo Comunicação finalizada!
  echo --------------------------------------------------------------
  rem Caso a criação da pasta ocorra sem nenhuma falha
  if %ERRORLEVEL% equ 0 (
    rem Informa ao usuário
    echo Pasta %backup_folder_path% criada com sucesso!
  rem Caso ocorra alguma falha na criação da pasta
  ) else (
    rem Informa ao usuário
    echo Erro ao criar a pasta %backup_folder_path%!
  )
)

echo Enviando arquivo %file_to_upload% para %backup_folder_path%...
echo --------------------------------------------------------------
echo Comunicando com o servidor FTP:
rem Realizando o upload do item para o caminho informado no servidor FTP
"winscp\WinSCP.com" /ini=nul /log=""%path_log_winscp%"" /command="option batch abort" "open %host_address% -explicittls -certificate="*"" "put ""%file_to_upload%"" ""%backup_folder_path%""" "exit"
echo Comunicação finalizada!
echo --------------------------------------------------------------

rem Caso o upload ocorra sem nenhuma falha
if %ERRORLEVEL% equ 0 (
  rem Informa ao usuário
  echo Upload finalizado com sucesso!
  echo ##############################################################
  rem Retorna a informação para o script python
  exit /b 0
rem Caso ocorra alguma falha no upload
) else (
  rem Informa ao usuário
  echo Upload finalizado com erro!
  echo ##############################################################
  rem Retorna a informação para o script python
  exit /b 1
)