# Script per creare collegamento sul Desktop con icona LEGO
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "LEGO BrickLink Analysis.lnk"
$targetPath = "C:\Development\Lego_Bricklink\Start_Lego_Webapp.bat"
$iconPath = "C:\Development\Lego_Bricklink\lego_icon.ico"

# Crea oggetto WScript.Shell
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)

# Configura il collegamento
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = "C:\Development\Lego_Bricklink"
$shortcut.Description = "Avvia LEGO BrickLink Analysis Web Server"
$shortcut.IconLocation = $iconPath

# Salva il collegamento
$shortcut.Save()

Write-Host "[OK] Collegamento creato sul Desktop!" -ForegroundColor Green
Write-Host "Percorso: $shortcutPath" -ForegroundColor Cyan
