# -*- coding: utf-8 -*-
"""
生成「合成安装器/触发样本」（C# 源码 -> csc.exe 编译成 exe）。
覆盖 PRD 中要求"构造样本"的验收项：A25 / A29 / A30 / F14 / F8。
用法: python sources/gen_csharp.py
"""
import os, subprocess, sys, tempfile, shutil

ROOT = os.environ.get("ATS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, "samples")
BUILD = os.path.join(ROOT, "sources", "csharp")
CSC = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
SENTINEL = r"C:\Users\Public\AT-SENTINEL"

# ---------------------------------------------------------------- 公共代码片段
PRELUDE = r"""
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
"""

# ---------------------------------------------------------------- 样本定义
# 键: (相对目录, 文件名, 需要WinForms)
SAMPLES_DEF = {}

# ============ 组 11：安装成功判定 A29 ============
SAMPLES_DEF[("samples/11-安装成功判定", "A29-01-假成功bootstrapper.exe", False)] = PRELUDE + r"""
// 只把载荷解到 %TEMP% 后 exit 0；无卸载项、无 watch_dirs 落盘。
// 期望：至多 install_unverified（A29 ①）——%TEMP% 在 watch_exclude 内，不得判 install_completed。
class P {
    static int Main(string[] args) {
        Env.Mark("A29-01");
        string dir = Path.Combine(Env.Temp, "A29_bootstrap_payload");
        Directory.CreateDirectory(dir);
        for (int i = 0; i < 8; i++)
            File.WriteAllText(Path.Combine(dir, "payload" + i + ".tmp"), new string('X', 4096));
        Env.Log("bootstrap: payload extracted to " + dir);
        Env.Log("installer finished.");
        return 0;   // 退出码 0，但零有效副作用
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-02-纯退出码0.exe", False)] = PRELUDE + r"""
// 立刻 exit 0，无任何副作用。期望 install_unverified（A29 ⑩ 底线保护）。
class P { static int Main(string[] args) { Env.Mark("A29-02"); Env.Log("nothing to do"); return 0; } }
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-03-标准安装-落盘+卸载项.exe", False)] = PRELUDE + r"""
// 在 Program Files 落盘 + 写 HKCU 卸载项 => S1 + S2 => install_completed / high
class P {
    static int Main(string[] args) {
        Env.Mark("A29-03");
        string loc = Path.Combine(Env.ProgramFiles, "ATSynthetic App A29-03");
        Directory.CreateDirectory(loc);
        File.WriteAllText(Path.Combine(loc, "app.exe"), "MZ" + new string('\0', 64));
        for (int i = 0; i < 20; i++)
            File.WriteAllText(Path.Combine(loc, "lib" + i + ".dll"), new string('D', 2048));
        Reg.WriteUninstall("ATSynthetic A29-03", "1.0.0", loc);
        Env.Log("Installed to " + loc);
        Env.Log("Installation completed successfully.");
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-04-per-user安装-HKCU卸载项.exe", False)] = PRELUDE + r"""
// 纯 per-user：只写 HKCU 卸载项 + %LOCALAPPDATA% 落盘。期望 install_completed（A29 ④）。
class P {
    static int Main(string[] args) {
        Env.Mark("A29-04");
        string loc = Path.Combine(Env.LocalAppData, "ATSyntheticPerUser");
        Directory.CreateDirectory(loc);
        File.WriteAllText(Path.Combine(loc, "app.exe"), "MZ" + new string('\0', 64));
        Reg.WriteUninstall("ATSynthetic A29-04 PerUser", "2.1.0", loc);
        Env.Log("Per-user install done: " + loc);
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-05-绿色便携-仅落盘.exe", False)] = PRELUDE + r"""
// 绿色便携：只落盘 %LOCALAPPDATA%，无卸载项 => S2 => install_completed / high
class P {
    static int Main(string[] args) {
        Env.Mark("A29-05");
        string loc = Path.Combine(Env.LocalAppData, "ATPortableA29");
        Directory.CreateDirectory(loc);
        for (int i = 0; i < 12; i++)
            File.WriteAllText(Path.Combine(loc, "portable" + i + ".dat"), new string('P', 1024));
        Env.Log("Portable extracted to " + loc);
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-06-反证据-失败码+回滚日志.exe", False)] = PRELUDE + r"""
// 退出码 1603（失败类）+ 回滚关键字，但有部分落盘 => install_partial + evidence_conflicts 非空（A29 ⑤）
class P {
    static int Main(string[] args) {
        Env.Mark("A29-06");
        string loc = Path.Combine(Env.ProgramFiles, "ATSynthetic Rollback");
        Directory.CreateDirectory(loc);
        File.WriteAllText(Path.Combine(loc, "half.dll"), new string('H', 1024));
        Env.Log("Installing...");
        Console.Error.WriteLine("Error 1603: fatal error during installation.");
        Console.Error.WriteLine("Rolling back changes...");
        Env.Log("Rollback completed. Installation failed.");
        return 1603;
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-07-反证据-装后回滚.exe", False)] = PRELUDE + r"""
// 先落盘并写卸载项 -> 退出 0 -> 由 detached 子进程 8s 后删除（模拟 MSI 事务回滚）。
// 期望：N6（新增目录在稳定期后被删除）/ N4（卸载项消失）=> install_partial，不得判成功。
class P {
    static int Main(string[] args) {
        Env.Mark("A29-07");
        string loc = Path.Combine(Env.LocalAppData, "ATRollbackA29");
        Directory.CreateDirectory(loc);
        for (int i = 0; i < 10; i++)
            File.WriteAllText(Path.Combine(loc, "f" + i + ".dat"), new string('R', 2048));
        Reg.WriteUninstall("ATSynthetic A29-07 Rollback", "1.0.0", loc);
        string kill = "ping -n 3 127.0.0.1 > nul & rmdir /s /q \"" + loc + "\"";
        Process.Start(new ProcessStartInfo("cmd.exe", "/c " + kill) { CreateNoWindow = true, UseShellExecute = false });
        Env.Log("Install done, then rollback scheduled.");
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-08-退出码1603失败.exe", False)] = PRELUDE + r"""
// 纯失败：退出码 1603、无任何落盘/注册表副作用 => failed（N1）
class P {
    static int Main(string[] args) {
        Env.Mark("A29-08");
        Console.Error.WriteLine("Error 1603: fatal error during installation.");
        return 1603;
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-09-覆盖升级-字段变化.exe", False)] = PRELUDE + r"""
// 重复运行：首次安装，再次运行时只改 DisplayVersion（A3 卸载项字段变化；升级豁免）
class P {
    static int Main(string[] args) {
        Env.Mark("A29-09");
        string key = "ATSynthetic A29-09 Upgrade";
        string loc = Path.Combine(Env.ProgramFiles, "ATSynthetic Upgrade A29-09");
        string prev = Reg.ReadVersion(key);
        if (prev == null) {
            Directory.CreateDirectory(loc);
            File.WriteAllText(Path.Combine(loc, "app.dll"), new string('U', 4096));
            Reg.WriteUninstall(key, "1.0.0", loc);
            Env.Log("Fresh install 1.0.0");
        } else {
            Reg.WriteUninstall(key, "2.0.0", loc);
            Env.Log("Upgraded " + prev + " -> 2.0.0");
        }
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-10-已安装检测-幂等.exe", False)] = PRELUDE + r"""
// 幂等安装器：第一次有副作用；第二次 diff 为空 => 期望 already_installed（A31 ⑤）
class P {
    static int Main(string[] args) {
        Env.Mark("A29-10");
        string key = "ATSynthetic A29-10 Idempotent";
        string loc = Path.Combine(Env.ProgramFiles, "ATSynthetic Idempotent A29-10");
        if (Reg.ReadVersion(key) != null && Directory.Exists(loc)) {
            Env.Log("Already installed, nothing to do.");
            return 0;
        }
        Directory.CreateDirectory(loc);
        for (int i = 0; i < 6; i++) File.WriteAllText(Path.Combine(loc, "m" + i + ".dat"), new string('I', 2048));
        Reg.WriteUninstall(key, "3.3.3", loc);
        Env.Log("Installed.");
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-11-口径对照-仅非卸载项注册表副作用.exe", False)] = PRELUDE + r"""
// 退出码 0（A1）+ 只在「非 Uninstall 根」写注册表，不落盘到任何 watch_dirs。
// 目的：暴露 PRD F15.7 「存在可归因副作用（落盘/注册表有变化）」的口径歧义 ——
//   若实现只把「Uninstall 根 diff / watch_dirs diff」算作副作用 -> 本样本 = 纯 A1 -> install_unverified（两个 profile 一致，底线保护）；
//   若实现把任何注册表写入都算副作用        -> loose 得 install_completed(medium)，strict 得 install_unverified(low)。
// 两种结果都需要人工判断是否合理；这正是 A29 ⑨ 要对照的点。
class P {
    static int Main(string[] args) {
        Env.Mark("A29-11");
        using (var k = Registry.CurrentUser.CreateSubKey(@"Software\AT-TestSuite\A29-11")) {
            k.SetValue("Installed", "1");
            k.SetValue("When", DateTime.Now.ToString("s"));
        }
        Env.Log("done (registry-only side effect, no watch_dirs change)");
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-11b-宽松口径-A1加落盘副作用.exe", False)] = PRELUDE + r"""
// 对照组：退出码 0 + 在 watch_dirs（%ProgramData%）落盘 -> 命中 S2 -> 两个 profile 都应 install_completed/high。
// 与 A29-11 配对，用来确认「落盘 = S 级」这条分界是否成立。
class P {
    static int Main(string[] args) {
        Env.Mark("A29-11b");
        string loc = Path.Combine(Env.ProgramData, "ATLooseSideEffectA29");
        Directory.CreateDirectory(loc);
        File.WriteAllText(Path.Combine(loc, "data.bin"), new string('L', 4096));
        Env.Log("done (watch_dirs side effect)");
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/11-安装成功判定", "A29-12-落盘到监控外目录.exe", False)] = PRELUDE + r"""
// 装到 watch_dirs 之外（C:\ATOutOfScope）=> 期望假阴性：triggered（F15.8 已知假阴性来源，用于验证边界）
class P {
    static int Main(string[] args) {
        Env.Mark("A29-12");
        string loc = @"C:\ATOutOfScope\A29-12";
        Directory.CreateDirectory(loc);
        for (int i = 0; i < 5; i++) File.WriteAllText(Path.Combine(loc, "o" + i + ".dat"), new string('O', 1024));
        Env.Log("installed to " + loc);
        return 0;
    }
}
"""

# ============ 组 12：超时与活动感知 A30 ============
SAMPLES_DEF[("samples/12-超时与活动感知", "A30-01-慢安装器-持续写盘90s.exe", False)] = PRELUDE + r"""
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
"""

SAMPLES_DEF[("samples/12-超时与活动感知", "A30-02-启动后无动作.exe", False)] = PRELUDE + r"""
// 启动后完全静止 300 秒（无窗口、无子进程、无写盘、无 CPU 增长）=> failed: no_activity(A30 ②)
class P {
    static int Main(string[] args) {
        Env.Mark("A30-02");
        Thread.Sleep(300000);
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/12-超时与活动感知", "A30-03-运行中静止.exe", False)] = PRELUDE + r"""
// 前 10 秒持续活动（写 %TEMP%，不在 watch_dirs 内 → 不产生 S 级证据），之后完全静止。
// 期望：idle_timeout 触发卡死判定并终止；最终 killed_on_timeout（无 watch_dirs 副作用）（A30 ②）。
class P {
    static int Main(string[] args) {
        Env.Mark("A30-03");
        string loc = Path.Combine(Env.Temp, "A30-03-progress");
        Directory.CreateDirectory(loc);
        for (int i = 0; i < 10; i++) {
            File.WriteAllText(Path.Combine(loc, "part" + i + ".dat"), new string('T', 32768));
            Env.Log("write " + i + " (to %TEMP%, not watched)");
            Thread.Sleep(1000);
        }
        Env.Log("now hanging silently...");
        Thread.Sleep(600000);
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/12-超时与活动感知", "A30-04-完成安装后卡在完成页.exe", False)] = PRELUDE + r"""
// 已完成安装（落盘 + 卸载项）后阻塞等待 => 超时终结，但 S 级证据已成立 => install_completed（A30 ④）
class P {
    static int Main(string[] args) {
        Env.Mark("A30-04");
        string loc = Path.Combine(Env.ProgramFiles, "ATDonePageA30");
        Directory.CreateDirectory(loc);
        for (int i = 0; i < 15; i++) File.WriteAllText(Path.Combine(loc, "f" + i + ".dat"), new string('D', 4096));
        Reg.WriteUninstall("ATSynthetic A30-04 DonePage", "1.0.0", loc);
        Env.Log("Installation completed. Waiting for user to click Finish...");
        Thread.Sleep(600000);
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/12-超时与活动感知", "A30-05-联网下载组件等待.exe", False)] = PRELUDE + r"""
// 模拟离线环境下"正在下载组件"卡住 => requires_network + 超时（F14.5 / A15）
class P {
    static int Main(string[] args) {
        Env.Mark("A30-05");
        Env.Log("Downloading required components from the Internet...");
        Env.Log("Connecting to download server ... 0%");
        for (int i = 0; i < 120; i++) {
            Thread.Sleep(5000);
            Env.Log("still downloading ... retry " + i);
        }
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/12-超时与活动感知", "A30-06-子进程脱离-进程树清理.exe", False)] = PRELUDE + r"""
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
"""

SAMPLES_DEF[("samples/12-超时与活动感知", "A30-07-超长安装-持续700s.exe", False)] = PRELUDE + r"""
// 持续 700 秒 > 单文件硬上限 600s => killed_on_timeout（A30 ⑤）
class P {
    static int Main(string[] args) {
        Env.Mark("A30-07");
        string loc = Path.Combine(Env.ProgramFiles, "ATVeryLongA30");
        Directory.CreateDirectory(loc);
        for (int i = 0; i < 140; i++) {
            File.WriteAllText(Path.Combine(loc, "seg" + i + ".dat"), new string('V', 65536));
            if (i % 10 == 0) Env.Log("segment " + i);
            Thread.Sleep(5000);
        }
        return 0;
    }
}
"""

# ============ 组 10：入口分层与黑名单 A25 / F17 ============
# 陷阱 exe：一旦被执行就留下铁证
for fn, tag in [
    ("unins000.exe", "BLACKLIST-unins000"),
    ("卸载.exe", "BLACKLIST-卸载"),
    ("uninstall.exe", "BLACKLIST-uninstall"),
    ("update.exe", "BLACKLIST-update"),
    ("updater.exe", "BLACKLIST-updater"),
    ("checkupdate.exe", "BLACKLIST-checkupdate"),
    ("crashpad_handler.exe", "BLACKLIST-crashpad"),
    ("crashreporter.exe", "BLACKLIST-crashreporter"),
    ("repair.exe", "BLACKLIST-repair"),
    ("debug-helper.exe", "BLACKLIST-debug"),
    ("modify.exe", "BLACKLIST-modify"),
]:
    SAMPLES_DEF[("_trap", fn, False)] = PRELUDE + (r"""
// 黑名单陷阱：被执行为重大失败（F17.3 / A25 ①）
class P {
    static int Main(string[] args) {
        Env.Mark("%s");
        try {
            Directory.CreateDirectory(Env.SENTINEL);
            File.WriteAllText(Path.Combine(Env.SENTINEL, "VIOLATION-%s.txt"),
                "该文件属于 F17.3 黑名单，绝不应被执行！\r\n" + DateTime.Now + "\r\n");
        } catch { }
        return 0;
    }
}
""" % (tag, tag))

# 正常入口（对照组，证明执行链本身可用）
SAMPLES_DEF[("_trap", "install.bat.exe", False)] = PRELUDE + r"""
class P {
    static int Main(string[] args) {
        Env.Mark("ENTRY-install");
        string loc = Path.Combine(Env.ProgramFiles, "ATPackageLayout A25");
        Directory.CreateDirectory(loc);
        File.WriteAllText(Path.Combine(loc, "installed.txt"), "ok");
        Reg.WriteUninstall("ATSynthetic A25 Package", "1.0.0", loc);
        Env.Log("package installer done");
        return 0;
    }
}
"""

# ============ 组 09：类型识别与伪装 ============
SAMPLES_DEF[("samples/09-类型识别与伪装", "伪装成exe的文本.exe", False)] = PRELUDE + r"""
class P { static int Main(string[] args) { Env.Mark("DISGUISE-text-as-exe"); return 0; } }
"""

# ============ 组 13/14：兜底 ============
SAMPLES_DEF[("samples/14-跳过与兜底", "未知扩展名-MZ头.bin", False)] = PRELUDE + r"""
class P { static int Main(string[] args) { Env.Mark("UNKNOWN-EXT-MZ"); Console.WriteLine("triggered unknown-ext PE"); return 0; } }
"""

SAMPLES_DEF[("samples/14-跳过与兜底", "无扩展名文件", False)] = PRELUDE + r"""
class P { static int Main(string[] args) { Env.Mark("NO-EXTENSION-PE"); Console.WriteLine("triggered no-extension PE"); return 0; } }
"""

SAMPLES_DEF[("samples/07-脚本与快捷方式", "scr-屏保触发器.scr", False)] = PRELUDE + r"""
class P { static int Main(string[] args) { Env.Mark("SCR"); Console.WriteLine("scr executed"); Thread.Sleep(1500); return 0; } }
"""

SAMPLES_DEF[("samples/07-脚本与快捷方式", "com-命令触发器.com", False)] = PRELUDE + r"""
class P { static int Main(string[] args) { Env.Mark("COM"); Console.WriteLine("com executed"); Thread.Sleep(1500); return 0; } }
"""

# ============ 组 20：F13 静默参数探测桩 ============
SAMPLES_DEF[("samples/12-超时与活动感知", "A30-08-GUI窗口-正在下载组件.exe", True)] = r"""
using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;
using System.Threading;

// 标准 WinForms 窗口，标题与内容都指向"正在下载组件"。
// 期望：F14.4 识别到"正在下载"语义 -> 记录 requires_network，并按静默期超时处理（A15）。
class DownloadWaiter : Form {
    ProgressBar bar;
    public DownloadWaiter() {
        Text = "正在下载组件...  Downloading components";
        ClientSize = new Size(460, 180);
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false; MinimizeBox = false;
        var lbl = new Label();
        lbl.Text = "正在从 Internet 下载所需组件，请稍候...\r\nDownloading required components from the Internet";
        lbl.SetBounds(20, 20, 420, 60);
        bar = new ProgressBar();
        bar.SetBounds(20, 90, 420, 24);
        bar.Style = ProgressBarStyle.Marquee;
        Controls.Add(lbl);
        Controls.Add(bar);
    }
    [STAThread]
    static void Main(string[] args) {
        try {
            Directory.CreateDirectory(@"C:\Users\Public\AT-SENTINEL");
            File.AppendAllText(@"C:\Users\Public\AT-SENTINEL\ran.log",
                DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  A30-08-DOWNLOAD-WINDOW\r\n");
        } catch { }
        Application.Run(new DownloadWaiter());
    }
}
"""

SAMPLES_DEF[("samples/12-超时与活动感知", "A30-09-超长安装-只在TEMP写盘700s.exe", False)] = PRELUDE + r"""
// 持续 700 秒，但只写 %TEMP%（不在 watch_dirs 内）=> 无 S 级证据 => 干净的 killed_on_timeout（A30 ⑤⑥）
class P {
    static int Main(string[] args) {
        Env.Mark("A30-09");
        string loc = Path.Combine(Env.Temp, "A30-09-long");
        Directory.CreateDirectory(loc);
        for (int i = 0; i < 140; i++) {
            File.WriteAllText(Path.Combine(loc, "seg" + i + ".dat"), new string('W', 65536));
            if (i % 20 == 0) Env.Log("segment " + i + " (temp only)");
            Thread.Sleep(5000);
        }
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/20-静默参数探测", "F13-参数探测桩-记录全部尝试.exe", False)] = PRELUDE + r"""
// 记录每次被调用时收到的完整命令行，然后以非零码退出（永不成功）。
// 用途：跑完后读哨兵日志，即可逐条核对 F13 静默参数表与轮询顺序（含"无参数运行"兜底那一跳）。
class P {
    static int Main(string[] args) {
        Env.Mark("F13-PROBE");
        try {
            Directory.CreateDirectory(Env.SENTINEL);
            string line = DateTime.Now.ToString("HH:mm:ss.fff") + "\t" +
                          (Env.HasSilentFlag() ? "[静默参数]" : "[无参数/GUI]") + "\t" +
                          string.Join(" ", args) + Environment.NewLine;
            File.AppendAllText(Path.Combine(Env.SENTINEL, "f13-argv.log"), line, Encoding.UTF8);
        } catch { }
        Env.Log("probe: args recorded, failing on purpose");
        return 1;   // 永不成功 -> 工具会继续尝试下一组参数
    }
}
"""

SAMPLES_DEF[("samples/20-静默参数探测", "F13-参数探测桩-见VERYSILENT即成功.exe", False)] = PRELUDE + r"""
// 记录命令行；仅当收到 Inno 家族静默参数时才算安装成功（落盘 + 卸载项），否则退出 1。
// 用途：验证 F13 第 5 条"任一尝试取得安装证据即提前结束该文件后续尝试"。
class P {
    static int Main(string[] args) {
        Env.Mark("F13-STOP");
        try {
            Directory.CreateDirectory(Env.SENTINEL);
            File.AppendAllText(Path.Combine(Env.SENTINEL, "f13-argv.log"),
                DateTime.Now.ToString("HH:mm:ss.fff") + "\t" +
                (Env.HasFlag("/VERYSILENT") ? "[命中 /VERYSILENT]" : "[未命中]") + "\t" +
                string.Join(" ", args) + Environment.NewLine, Encoding.UTF8);
        } catch { }
        if (!Env.HasFlag("/VERYSILENT") && !Env.HasFlag("/verysilent")) {
            Env.Log("probe: not my silent flag, failing");
            return 1;
        }
        string loc = Path.Combine(Env.ProgramFiles, "ATF13Stub");
        Directory.CreateDirectory(loc);
        File.WriteAllText(Path.Combine(loc, "installed.txt"), "ok");
        Reg.WriteUninstall("ATF13Stub", "1.0.0", loc);
        Env.Log("probe: installed with /VERYSILENT");
        return 0;
    }
}
"""

SAMPLES_DEF[("samples/20-静默参数探测", "F13-参数探测桩-只认NSIS的S.exe", False)] = PRELUDE + r"""
// 只认 NSIS 的 /S；用来观察工具是否在 Inno 参数失败后继续尝试 NSIS 参数。
class P {
    static int Main(string[] args) {
        Env.Mark("F13-NSIS");
        try {
            Directory.CreateDirectory(Env.SENTINEL);
            File.AppendAllText(Path.Combine(Env.SENTINEL, "f13-argv.log"),
                DateTime.Now.ToString("HH:mm:ss.fff") + "\t" +
                (Env.HasFlag("/S") ? "[命中 /S]" : "[未命中]") + "\t" +
                string.Join(" ", args) + Environment.NewLine, Encoding.UTF8);
        } catch { }
        if (!Env.HasFlag("/S")) { Env.Log("probe: no /S"); return 1; }
        string loc = Path.Combine(Env.ProgramData, "ATF13Nsis");
        Directory.CreateDirectory(loc);
        File.WriteAllText(Path.Combine(loc, "installed.txt"), "ok");
        Reg.WriteUninstall("ATF13Nsis", "1.0.0", loc);
        Env.Log("probe: installed with /S");
        return 0;
    }
}
"""

# ============ 组 07：DLL 导出 ============
SAMPLES_DEF[("samples/07-脚本与快捷方式", "触发用导出库.dll", True)] = None  # 占位，单独编译

# ============ 组 16：自绘界面（走模板/OCR 路径，无 UIA 控件树）============
OWNERDRAW_COMMON = r"""
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;
using System.Text;
using System.Windows.Forms;
using Microsoft.Win32;

// 完全自绘的无边框窗口：没有任何子控件 => UIA 拿不到控件树，
// 只能靠图像模板 / OCR 定位文本像素位（F14.2 二级/三级策略）。
class OwnerDrawInstaller : Form {
    int step = 0;
    Rectangle btnNext, btnAccept, chkAgree;
    bool agreed = false;
    bool dark;
    public OwnerDrawInstaller(bool isDark, string title) {
        dark = isDark;
        Text = title;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        StartPosition = FormStartPosition.CenterScreen;
        ClientSize = new Size(560, 380);
        MaximizeBox = false; MinimizeBox = false;
        SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint | ControlStyles.OptimizedDoubleBuffer, true);
        btnNext = new Rectangle(400, 320, 130, 34);
        chkAgree = new Rectangle(40, 250, 20, 20);
    }
    Color Bg { get { return dark ? Color.FromArgb(32, 32, 32) : Color.FromArgb(240, 240, 240); } }
    Color Fg { get { return dark ? Color.FromArgb(240, 240, 240) : Color.FromArgb(20, 20, 20); } }
    protected override void OnPaint(PaintEventArgs e) {
        var g = e.Graphics;
        g.SmoothingMode = SmoothingMode.AntiAlias;
        g.Clear(Bg);
        using (var f = new Font("Microsoft YaHei UI", 11, FontStyle.Regular))
        using (var fb = new Font("Microsoft YaHei UI", 11, FontStyle.Bold))
        using (var b = new SolidBrush(Fg)) {
            if (step == 0) {
                g.DrawString("欢迎使用 自绘界面 安装向导", new Font("Microsoft YaHei UI", 15, FontStyle.Bold), b, 36, 36);
                g.DrawString("本窗口没有任何标准控件，UIA 无法枚举。", f, b, 36, 90);
                g.DrawString("请勾选【我接受协议】后点击【下一步】。", f, b, 36, 125);
                g.DrawRectangles(new Pen(Fg, 2), new[] { new RectangleF(chkAgree.X, chkAgree.Y, chkAgree.Width, chkAgree.Height) });
                if (agreed) {
                    using (var p = new Pen(Color.FromArgb(0, 120, 215), 3))
                        g.DrawLines(p, new[] { new Point(chkAgree.X + 4, chkAgree.Y + 10), new Point(chkAgree.X + 9, chkAgree.Y + 15), new Point(chkAgree.X + 16, chkAgree.Y + 4) });
                }
                g.DrawString("我接受协议  /  I accept the agreement", f, b, 70, 249);
                DrawButton(g, btnNext, "下一步  Next", fb);
            } else if (step == 1) {
                g.DrawString("选择安装位置", new Font("Microsoft YaHei UI", 15, FontStyle.Bold), b, 36, 36);
                g.DrawString("目标文件夹：C:\\Program Files\\ATOwnerDraw", f, b, 36, 90);
                g.DrawString("点击【安装】开始安装。", f, b, 36, 125);
                DrawButton(g, btnNext, "安装  Install", fb);
            } else {
                g.DrawString("安装完成", new Font("Microsoft YaHei UI", 15, FontStyle.Bold), b, 36, 36);
                g.DrawString("软件已成功安装到本机。", f, b, 36, 90);
                DrawButton(g, btnNext, "完成  Finish", fb);
            }
        }
        using (var p = new Pen(Color.FromArgb(0, 120, 215), 1))
            g.DrawRectangle(p, 0, 0, ClientSize.Width - 1, ClientSize.Height - 1);
    }
    void DrawButton(Graphics g, Rectangle r, string text, Font f) {
        using (var b = new LinearGradientBrush(r, Color.FromArgb(0, 120, 215), Color.FromArgb(0, 90, 170), 90f))
            g.FillRectangle(b, r);
        using (var sf = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center })
        using (var w = new SolidBrush(Color.White))
            g.DrawString(text, f, w, r, sf);
    }
    protected override void OnMouseDown(MouseEventArgs e) {
        if (btnNext.Contains(e.Location)) {
            step++;
            if (step == 2) DoInstall();
            Invalidate();
        } else if (chkAgree.Contains(e.Location)) {
            agreed = !agreed; Invalidate();
        }
    }
    void DoInstall() {
        try {
            string loc = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "ATOwnerDraw");
            Directory.CreateDirectory(loc);
            for (int i = 0; i < 10; i++) File.WriteAllText(Path.Combine(loc, "f" + i + ".dat"), new string('G', 4096));
            using (var k = Registry.CurrentUser.CreateSubKey(@"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATOwnerDraw")) {
                k.SetValue("DisplayName", "ATOwnerDraw Synthetic");
                k.SetValue("DisplayVersion", "1.0.0");
                k.SetValue("InstallLocation", loc);
            }
        } catch { }
    }
    [STAThread]
    static void Main(string[] args) {
        try {
            Directory.CreateDirectory(@"C:\Users\Public\AT-SENTINEL");
            File.AppendAllText(@"C:\Users\Public\AT-SENTINEL\ran.log", DateTime.Now + "  OWNERDRAW\r\n");
        } catch { }
        bool dark = args.Length > 0 && args[0] == "dark";
        Application.EnableVisualStyles();
        Application.Run(new OwnerDrawInstaller(dark, "自绘界面安装向导 Synthetic"));
    }
}
"""

SAMPLES_DEF[("samples/16-自绘界面-OCR专项", "OWNERDRAW-自绘向导-浅色.exe", True)] = OWNERDRAW_COMMON
SAMPLES_DEF[("samples/16-自绘界面-OCR专项", "OWNERDRAW-自绘向导-深色.exe", True)] = OWNERDRAW_COMMON.replace(
    "OwnerDrawInstaller(bool isDark, string title)", "OwnerDrawInstaller(bool isDark, string title)")


# ---------------------------------------------------------------- 编译
def compile_one(rel_dir, filename, need_winforms, src, force=False):
    out_dir = os.path.join(ROOT, rel_dir)
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, filename)
    if os.path.exists(target) and not force:
        return ("SKIP", filename, os.path.getsize(target))
    src_path = os.path.join(BUILD, filename.replace("\\", "_") + ".cs")
    with open(src_path, "w", encoding="utf-8-sig") as f:
        f.write(src)
    exe_tmp = os.path.join(BUILD, "_tmp.exe")
    dbg_tmp = os.path.join(BUILD, "_tmp.pdb")
    cmd = [CSC, "/nologo", "/target:exe", "/platform:anycpu", "/optimize+",
           "/codepage:65001", "/out:" + exe_tmp, src_path]
    if need_winforms:
        cmd[2:2] = ["/target:winexe"]
        cmd = [c for c in cmd if c != "/target:exe"]
        cmd += ["/r:System.Windows.Forms.dll", "/r:System.Drawing.dll"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        return ("FAIL", filename, (p.stdout or "") + (p.stderr or ""))
    shutil.move(exe_tmp, target)
    for junk in (dbg_tmp,):
        if os.path.exists(junk):
            os.remove(junk)
    return ("OK", filename, os.path.getsize(target))


def main():
    os.makedirs(BUILD, exist_ok=True)
    try:                      # 哨兵目录由样本在测试运行时自行创建；此处仅尽力而为
        os.makedirs(SENTINEL, exist_ok=True)
    except OSError as e:
        print("提示: 无法预建哨兵目录 %s (%s)，样本运行时会自行创建。" % (SENTINEL, e))
    if not os.path.exists(CSC):
        print("找不到 csc.exe: " + CSC)
        return 1
    ok = fail = skip = 0
    for (rel_dir, filename, wf), src in SAMPLES_DEF.items():
        if src is None:
            continue
        st, name, info = compile_one(rel_dir, filename, wf, src)
        if st == "OK":
            ok += 1
            print("[OK]   %-52s %8d" % (name, info))
        elif st == "SKIP":
            skip += 1
        else:
            fail += 1
            print("[FAIL] %-52s\n%s" % (name, info[:1500]))
    print("\n编译完成: 新增 %d / 跳过 %d / 失败 %d" % (ok, skip, fail))
    print("哨兵目录: " + SENTINEL)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
