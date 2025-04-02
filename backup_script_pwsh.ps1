
Start-Sleep -Seconds 5
# todo: put this in a dedicated file for reuse and dot-source the file
function Test-Administrator {  
    [OutputType([bool])]
    param()
    process {
        [Security.Principal.WindowsPrincipal]$user = [Security.Principal.WindowsIdentity]::GetCurrent();
        return $user.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator);
    }
}

if (-not (Test-Administrator)) {
    # TODO: define proper exit codes for the given errors 
    Write-Error "O script precisa ser executado como administrador.";
    exit 1;
}

$ErrorActionPreference = "Stop";

Start-Sleep -Seconds 5