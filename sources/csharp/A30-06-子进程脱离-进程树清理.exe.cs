
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

// 父进程拉起一个 detached 子进程持续写盘，父进程 8 秒后退出 => 验证 Job Object 进程树清理（A4 / A30 ③）
class P {
    static int Main(string[] args) {
        Env.Mark("A30-06");
        string child = "ping -n 400 127.0.0.1 > nul & echo child-alive >> \"" +
                       Path.Combine(Env.SENTINEL, "child-alive.txt") + "\"";
        Process.Start(new ProcessStartInfo("cmd.exe", "/c " + child) {
            CreateNoWindow = true, UseShellExecute = false
        });
        Env.Log("spawned detached child");
        Thread.Sleep(8000);
        Env.Log("parent exiting");
        return 0;
    }
}
