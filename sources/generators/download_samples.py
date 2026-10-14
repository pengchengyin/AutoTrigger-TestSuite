# -*- coding: utf-8 -*-
"""
测试样本下载器（可断点续传/重试）。
用法: python _download.py [--force]
"""
import os, ssl, sys, time, threading, urllib.request, urllib.error, concurrent.futures

ROOT = os.environ.get("ATS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# (相对目录, 文件名, URL)
TARGETS = [
    # ===== 工具链：用于构造合成样本（不属于样本本身）=====
    ("_toolchain/choco", "innosetup.nupkg",   "https://community.chocolatey.org/api/v2/package/innosetup"),
    ("_toolchain/choco", "nsis.nupkg",        "https://community.chocolatey.org/api/v2/package/nsis"),
    ("_toolchain/wix",   "wix314-binaries.zip", "https://github.com/wixtoolset/wix3/releases/download/wix3141rtm/wix314-binaries.zip"),

    # ===== 01 Inno Setup 家族 =====
    ("samples/01-Inno Setup", "WinSCP-6.3.6-Setup.exe", "https://winscp.net/download/WinSCP-6.3.6-Setup.exe"),
    ("samples/01-Inno Setup", "WinMerge-2.16.46-x64-Setup.exe", "https://github.com/WinMerge/winmerge/releases/download/v2.16.46/WinMerge-2.16.46-x64-Setup.exe"),
    ("samples/01-Inno Setup", "Git-2.47.1-64-bit.exe", "https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/Git-2.47.1-64-bit.exe"),

    # ===== 02 NSIS 家族 =====
    ("samples/02-NSIS", "npp.8.8.1.Installer.x64.exe", "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.8.1/npp.8.8.1.Installer.x64.exe"),
    ("samples/02-NSIS", "Everything-1.4.1.1026.x64-Setup.exe", "https://www.voidtools.com/Everything-1.4.1.1026.x64-Setup.exe"),
    ("samples/02-NSIS", "audacity-win-3.7.1-64bit.exe", "https://github.com/audacity/audacity/releases/download/Audacity-3.7.1/audacity-win-3.7.1-64bit.exe"),
    ("samples/02-NSIS", "Firefox-Setup-zh-CN.exe", "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=zh-CN"),

    # ===== 03 MSI / WiX =====
    ("samples/03-MSI", "7z2600-x64.msi", "https://www.7-zip.org/a/7z2600-x64.msi"),
    ("samples/03-MSI", "putty-64bit-0.85-installer.msi", "https://the.earth.li/~sgtatham/putty/0.85/w64/putty-64bit-0.85-installer.msi"),
    ("samples/03-MSI", "node-v22.11.0-x64.msi", "https://nodejs.org/dist/v22.11.0/node-v22.11.0-x64.msi"),
    ("samples/03-MSI", "TortoiseGit-2.17.0.0-64bit.msi", "https://download.tortoisegit.org/tgit/2.17.0.0/TortoiseGit-2.17.0.0-64bit.msi"),
    ("samples/03-MSI", "KeePassXC-2.7.9-Win64.msi", "https://github.com/keepassxreboot/keepassxc/releases/download/2.7.9/KeePassXC-2.7.9-Win64.msi"),

    # ===== 04 Burn bootstrapper =====
    ("samples/04-Burn bootstrapper", "python-3.13.0-amd64.exe", "https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe"),
    ("samples/04-Burn bootstrapper", "VC_redist.x64.exe", "https://aka.ms/vs/17/release/vc_redist.x64.exe"),
    ("samples/04-Burn bootstrapper", "windowsdesktop-runtime-8.0-win-x64.exe", "https://aka.ms/dotnet/8.0/windowsdesktop-runtime-win-x64.exe"),

    # ===== 05 InstallShield / 其它家族 =====
    ("samples/05-InstallShield", "MobaXterm_Installer.zip", "https://download.mobatek.net/2422024090615612/MobaXterm_Installer_v24.2.zip"),

    # ===== 06 压缩包 =====
    ("samples/06-压缩包", "nssm-2.24.zip", "https://nssm.cc/release/nssm-2.24.zip"),
    ("samples/06-压缩包", "putty-0.85-w64.zip", "https://the.earth.li/~sgtatham/putty/0.85/w64/putty.zip"),
    ("samples/06-压缩包", "7z2501-extra.7z", "https://www.7-zip.org/a/7z2501-extra.7z"),
    ("samples/06-压缩包", "npp.8.8.1.portable.x64.zip", "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.8.1/npp.8.8.1.portable.x64.zip"),
    ("samples/06-压缩包", "7z2600-x64-32bit.exe", "https://www.7-zip.org/a/7z2600.exe"),
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
lock = threading.Lock()


def human(n):
    return "%.1fMB" % (n / 1048576.0) if n else "?"


def already_ok(path):
    """用 .ok 标记文件记录完成，避免重复下载。"""
    return os.path.exists(path + ".ok")


def fetch(item):
    reldir, name, url = item
    destdir = os.path.join(ROOT, reldir)
    os.makedirs(destdir, exist_ok=True)
    dest = os.path.join(destdir, name)
    if already_ok(dest):
        with lock:
            print("[SKIP] %s (已完成)" % name, flush=True)
        return (True, name, os.path.getsize(dest))
    if url is None:
        return (False, name, 0)
    headers = {"User-Agent": UA, "Accept": "*/*", "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}
    last = None
    for attempt in range(1, 5):
        tmp = dest + ".part"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=90, context=ctx) as r, open(tmp, "wb") as f:
                total = r.headers.get("Content-Length")
                total = int(total) if total else 0
                got = 0
                t0 = time.time()
                while True:
                    chunk = r.read(262144)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
            os.replace(tmp, dest)
            open(dest + ".ok", "w").write("%s\n%s\n" % (url, got))
            with lock:
                print("[ OK ] %-42s %8s  (%.1fs)" % (name, human(got), time.time() - t0), flush=True)
            return (True, name, got)
        except Exception as e:
            last = "%s: %s" % (type(e).__name__, str(e)[:120])
            try:
                os.remove(tmp)
            except OSError:
                pass
            time.sleep(2 * attempt)
    with lock:
        print("[FAIL] %-42s %s" % (name, last), flush=True)
    return (False, name, 0)


if __name__ == "__main__":
    if "--force" in sys.argv:
        for reldir, name, _ in TARGETS:
            p = os.path.join(ROOT, reldir, name + ".ok")
            if os.path.exists(p):
                os.remove(p)
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(fetch, TARGETS))
    okn = sum(1 for r in res if r[0])
    total = sum(r[2] for r in res)
    print("\n===== 下载汇总: 成功 %d / %d, 合计 %s, 耗时 %.1fs =====" %
          (okn, len(res), human(total), time.time() - t0), flush=True)
    for ok, name, size in res:
        if not ok:
            print("  未完成: %s" % name)
