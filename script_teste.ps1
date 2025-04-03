$vm_to_backup = $args[0]
#Write-Host $vm_to_backup

# TestDelay:
Write-Host "Iniciando script de backup..."
#Start-Sleep -Seconds 1

# Get the ID and security principal of the current user account
$myWindowsID = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$myWindowsPrincipal = new-object System.Security.Principal.WindowsPrincipal($myWindowsID)

# Get the security principal for the Administrator role
$adminRole = [System.Security.Principal.WindowsBuiltInRole]::Administrator
  
# Check to see if we are currently running "as Administrator"
if ($myWindowsPrincipal.IsInRole($adminRole)) {
    Write-Host "Script rodando como Administrador!";
    # We are running "as Administrator" - so change the title and background color to indicate this
    $Host.UI.RawUI.WindowTitle = $myInvocation.MyCommand.Definition + "(Elevated)"
    # $Host.UI.RawUI.BackgroundColor = "DarkBlue"
    clear-host
}
else {
    Write-Host "Elevando acesso do script para Administrador...";
    # We are not running "as Administrator" - so relaunch as administrator
    
    # Create a new process object that starts PowerShell
    $newProcess = new-object System.Diagnostics.ProcessStartInfo "PowerShell";
    
    # Specify the current script path and name as a parameter
    $newProcess.Arguments = $myInvocation.MyCommand.Definition;
    
    # Indicate that the process should be elevated
    $newProcess.Verb = "runas";
    
    # Start the new process
    [System.Diagnostics.Process]::Start($newProcess).WaitForExit();
}


# Run your code that needs to be elevated here
$base_path_for_backups = "C:\vm_backups\"
$vm_path_for_backup = $vm_to_backup + "_bkp"
$path_for_backup = Join-Path $base_path_for_backups $vm_path_for_backup
New-Item -ItemType Directory -Force -Path $path_for_backup

#Export-VM -Name $vm_to_backup -Path $path_for_backup

# TestDelay:
#Write-Host "Script rodando..."
#Start-Sleep -Seconds 1