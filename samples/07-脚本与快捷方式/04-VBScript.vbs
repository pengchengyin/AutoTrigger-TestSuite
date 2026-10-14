Set fso = CreateObject("Scripting.FileSystemObject")
If Not fso.FolderExists("C:\Users\Public\AT-SENTINEL") Then fso.CreateFolder("C:\Users\Public\AT-SENTINEL")
Set f = fso.OpenTextFile("C:\Users\Public\AT-SENTINEL\ran.log", 8, True)
f.WriteLine "SCRIPT-vbs"
f.Close
WScript.Echo "vbs executed"
