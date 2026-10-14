var fso = new ActiveXObject("Scripting.FileSystemObject");
if (!fso.FolderExists("C:\Users\Public\AT-SENTINEL")) fso.CreateFolder("C:\Users\Public\AT-SENTINEL");
var f = fso.OpenTextFile("C:\Users\Public\AT-SENTINEL\\ran.log", 8, true); f.WriteLine("SCRIPT-js"); f.Close();
WScript.Echo("js executed");
