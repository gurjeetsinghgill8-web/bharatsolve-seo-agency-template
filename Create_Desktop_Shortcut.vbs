' BHARATSOLVE - Create Desktop Shortcut
' Double-click this ONCE to add shortcut to your desktop

Set shell = CreateObject("WScript.Shell")
desktop = shell.SpecialFolders("Desktop")

Set shortcut = shell.CreateShortcut(desktop & "\BHARATSOLVE SEO AGENCY.lnk")
shortcut.TargetPath = CreateObject("Scripting.FileSystemObject").GetAbsolutePathName(".") & "\BHARATSOLVE_Launcher.bat"
shortcut.WorkingDirectory = CreateObject("Scripting.FileSystemObject").GetAbsolutePathName(".")
shortcut.Description = "BHARATSOLVE SEO AGENCY - AI Powered Single Person SEO Agency"
shortcut.Save()

MsgBox "✅ Desktop shortcut created!" & vbCrLf & vbCrLf & "Look for 'BHARATSOLVE SEO AGENCY' on your desktop.", vbInformation, "BHARATSOLVE"
