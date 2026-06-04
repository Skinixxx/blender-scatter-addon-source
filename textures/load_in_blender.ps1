Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Diagnostics;
public class WinAPI {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

$proc = Get-Process blender -ErrorAction SilentlyContinue
if (-not $proc) { Write-Host "Blender not found"; exit 1 }

$hwnd = $proc.MainWindowHandle
[WinAPI]::ShowWindow($hwnd, 1) | Out-Null
[WinAPI]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 500

[System.Windows.Forms.SendKeys]::SendWait("^{TAB}")  # Switch workspace
Start-Sleep -Milliseconds 300
[System.Windows.Forms.SendKeys]::SendWait("^{TAB}")  
Start-Sleep -Milliseconds 300
[System.Windows.Forms.SendKeys]::SendWait("^{TAB}")  
Start-Sleep -Milliseconds 300
[System.Windows.Forms.SendKeys]::SendWait("^{TAB}")  
Start-Sleep -Milliseconds 500

# Open Text Editor (Shift+F11)
[System.Windows.Forms.SendKeys]::SendWait("+{F11}")
Start-Sleep -Milliseconds 500

# Open file (Alt+T, then select Open)
[System.Windows.Forms.SendKeys]::SendWait("%T")  
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("O")  
Start-Sleep -Milliseconds 500

# Type file path
$path = "C:\Users\skinix\cursach\textures\load_textures.py"
[System.Windows.Forms.SendKeys]::SendWait($path)
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("~")
Start-Sleep -Milliseconds 1000

# Run Script (Alt+P)
[System.Windows.Forms.SendKeys]::SendWait("%P")
Write-Host "Script sent to Blender!"
