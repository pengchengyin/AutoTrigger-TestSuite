
using System;
using System.IO;
using System.Text;
using System.Threading;
using System.Diagnostics;
using System.Collections.Generic;
using Microsoft.Win32;

static class Env {
    public const string SENTINEL = @"C:\Users\Public\AT-SENTINEL";
    public static void Mark(string tag) {
        try {
            Directory.CreateDirectory(SENTINEL);
            File.AppendAllText(Path.Combine(SENTINEL, "ran.log"),
                DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + tag + "\r\n", Encoding.UTF8);
        } catch { }
    }
    public static void Log(string msg) {
        Console.Out.WriteLine(msg);
        Console.Out.Flush();
    }
    public static bool HasFlag(string flag) {
        foreach (var a in Environment.GetCommandLineArgs())
            if (string.Equals(a, flag, StringComparison.OrdinalIgnoreCase)) return true;
        return false;
    }
    public static bool HasSilentFlag() {
        string[] flags = { "/VERYSILENT", "/verysilent", "/S", "/s", "/silent", "/quiet",
                           "--silent", "--quiet", "-s", "/qn", "/Q", "/quiet /norestart" };
        foreach (var a in Environment.GetCommandLineArgs())
            foreach (var f in flags)
                if (string.Equals(a, f, StringComparison.OrdinalIgnoreCase)) return true;
        return false;
    }
    public static string LocalAppData { get { return Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData); } }
    public static string AppData { get { return Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData); } }
    public static string ProgramData { get { return Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData); } }
    public static string ProgramFiles { get { return Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles); } }
    public static string Temp { get { return Path.GetTempPath(); } }
}

static class Reg {
    /// <summary>写 HKCU 卸载项（验证 F15.1 S1「必须含 HKCU」）。</summary>
    public static void WriteUninstall(string name, string version, string location) {
        using (var k = Registry.CurrentUser.CreateSubKey(
            @"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\" + name)) {
            k.SetValue("DisplayName", name);
            k.SetValue("DisplayVersion", version);
            k.SetValue("InstallLocation", location);
            k.SetValue("UninstallString", "\"" + Path.Combine(location, "unins000.exe") + "\"");
            k.SetValue("Publisher", "AT-TestSuite");
        }
    }
    public static void DeleteUninstall(string name) {
        try { Registry.CurrentUser.DeleteSubKeyTree(
            @"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\" + name, false); } catch { }
    }
    public static string ReadVersion(string name) {
        using (var k = Registry.CurrentUser.OpenSubKey(
            @"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\" + name)) {
            return k == null ? null : (string)k.GetValue("DisplayVersion");
        }
    }
}

// 每 3 秒写一个文件，持续 90 秒（> idle_timeout 60s，< timeout 600s）。期望：不误杀，正常完成（A30 ①）
class P {
    static int Main(string[] args) {
        Env.Mark("A30-01");
        string loc = Path.Combine(Env.ProgramFiles, "ATSlowInstaller A30-01");
        Directory.CreateDirectory(loc);
        for (int i = 0; i < 30; i++) {
            File.WriteAllText(Path.Combine(loc, "chunk" + i + ".dat"), new string('S', 65536));
            Env.Log("write chunk " + i + " (" + (i + 1) + "/30)");
            Thread.Sleep(3000);
        }
        Reg.WriteUninstall("ATSynthetic A30-01 Slow", "1.0.0", loc);
        Env.Log("slow installer finished");
        return 0;
    }
}
