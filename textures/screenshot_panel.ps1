Add-Type -AssemblyName System.Drawing
$code = @'
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class SS {
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hDC, uint nFlags);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    public static Rectangle GetWindowRect(IntPtr hWnd) { RECT r; GetWindowRect(hWnd, out r); return new Rectangle(r.Left, r.Top, r.Right - r.Left, r.Bottom - r.Top); }
    public static void BringToFront(IntPtr hWnd) { ShowWindow(hWnd, 9); SetForegroundWindow(hWnd); }
}
'@
Add-Type -TypeDefinition $code -ReferencedAssemblies "System.Drawing.dll"

$proc = Get-Process blender -ErrorAction SilentlyContinue
if (-not $proc) { Write-Host "NO_BLENDER"; exit 1 }
$hwnd = $proc.MainWindowHandle

[SS]::BringToFront($hwnd)
Start-Sleep -Milliseconds 500

# Press N to open sidebar
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("n")
Start-Sleep -Milliseconds 1000

$r = [SS]::GetWindowRect($hwnd)
$bmp = New-Object System.Drawing.Bitmap ($r.Width, $r.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.Left, $r.Top, 0, 0, $bmp.Size)
$bmp.Save("C:\Users\skinix\cursach\screenshot_panel.png")
$g.Dispose(); $bmp.Dispose()
Write-Host "PANEL_SCREENSHOT_OK"
