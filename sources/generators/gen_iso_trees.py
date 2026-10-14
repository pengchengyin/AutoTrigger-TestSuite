# -*- coding: utf-8 -*-
"""
构造 ISO 源目录树（覆盖 F18.1 五种介质性质判定 + F18.5 autorun 衔接 + A26/A27）。
随后由 sources/gen_iso.ps1 用 IMAPI2FS 打包成 .iso。
用法: python sources/gen_iso_trees.py
"""
import os, shutil

ROOT = os.environ.get("ATS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "samples")
TREES = os.path.join(ROOT, "sources", "iso", "trees")
TRAP = os.path.join(ROOT, "_trap")
PAYLOAD = os.path.join(ROOT, "sources", "payload")


def W(path, data=b"", ):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    return path


def tree(name):
    p = os.path.join(TREES, name)
    if os.path.isdir(p):
        shutil.rmtree(p, ignore_errors=True)
    os.makedirs(p, exist_ok=True)
    return p


def real_pe():
    for c in [os.path.join(TRAP, "install.bat.exe"), os.path.join(PAYLOAD, "app.exe")]:
        if os.path.exists(c):
            return open(c, "rb").read()
    raise SystemExit("缺少可用 PE")


PE = None

README_TXT = ("安装说明 / Installation Notes\r\n"
              "============================\r\n"
              "双击 install.bat 开始安装。\r\n"
              "Run setup.exe /S for silent installation.\r\n")

AUTORUN_GOOD = "[AutoRun]\r\nopen=setup.exe\r\nicon=setup.exe,0\r\nshellexecute=setup.exe\r\n"
AUTORUN_MISSING = "[AutoRun]\r\nopen=missing-installer.exe\r\nicon=missing.ico,0\r\n"


def build_all():
    global PE
    PE = real_pe()

    # ---- A26-01 installer_media：autorun.inf 指向 setup.exe（P0）----
    t = tree("A26-01-installer_media")
    W(os.path.join(t, "autorun.inf"), AUTORUN_GOOD)
    W(os.path.join(t, "setup.exe"), PE)
    W(os.path.join(t, "install.bat"),
      "@echo off\r\necho ISO-install.bat >> \"C:\\Users\\Public\\AT-SENTINEL\\ran.log\"\r\nexit /b 0\r\n")
    W(os.path.join(t, "安装说明.txt"), README_TXT)
    W(os.path.join(t, "data", "resource.dat"), b"D" * 4096)
    W(os.path.join(t, "unins000.exe"), PE)      # 黑名单，验证不被执行
    print("[OK] A26-01-installer_media")

    # ---- A26-02 malware_lure：仅 1 个 .lnk + 载荷（隐藏）----
    t = tree("A26-02-malware_lure")
    W(os.path.join(t, "payload.exe"), PE)
    W(os.path.join(t, "发票明细.exe"), PE)
    # .lnk 由 gen_lnk.ps1 在同目录内生成，保证相对路径可解析
    print("[OK] A26-02-malware_lure (lnk 由 gen_lnk.ps1 补)")

    # ---- A26-03 os_install_media：含 sources\\install.wim -> 默认跳过 ----
    t = tree("A26-03-os_install_media")
    W(os.path.join(t, "sources", "install.wim"), b"WIM-DUMMY" + b"\0" * 8192)
    W(os.path.join(t, "sources", "setup.exe"), PE)
    W(os.path.join(t, "boot", "bcd"), b"BCD-DUMMY" + b"\0" * 512)
    W(os.path.join(t, "setup.exe"), PE)
    W(os.path.join(t, "autorun.inf"), AUTORUN_GOOD)
    W(os.path.join(t, "bootmgr"), b"MZ" + b"\0" * 512)
    print("[OK] A26-03-os_install_media")

    # ---- A26-04 media_disc：蓝光/影碟特征 -> 默认跳过 ----
    t = tree("A26-04-media_disc")
    W(os.path.join(t, "BDMV", "STREAM", "00001.m2ts"), b"M2TS" + b"\0" * 4096)
    W(os.path.join(t, "BDMV", "index.bdmv"), b"INDX0200" + b"\0" * 256)
    W(os.path.join(t, "VIDEO_TS", "VTS_01_1.VOB"), b"VOB" + b"\0" * 4096)
    W(os.path.join(t, "VIDEO_TS", "VIDEO_TS.IFO"), b"DVDVIDEO" + b"\0" * 256)
    print("[OK] A26-04-media_disc")

    # ---- A26-05 data_disc：普通数据盘 ----
    t = tree("A26-05-data_disc")
    for i in range(6):
        W(os.path.join(t, "docs", "file%02d.txt" % i), "data disc file %d\r\n" % i)
    W(os.path.join(t, "photos", "image01.jpg"), b"\xff\xd8\xff\xe0" + b"\0" * 1024)
    W(os.path.join(t, "setup.exe"), PE)
    W(os.path.join(t, "readme.txt"), "普通数据光盘\r\n")
    print("[OK] A26-05-data_disc")

    # ---- A26-06 乱码文件名（GBK 被按 Latin-1 显示的样子）+ 正常 setup.exe ----
    t = tree("A26-06-garbled-names")
    # 经典 GBK→Latin1 乱码串（"安装说明" 的 GBK 字节按 cp1252 呈现）
    garble = "°²×°ËµÃ÷.txt"
    W(os.path.join(t, garble), README_TXT)
    W(os.path.join(t, "ÉèÖÃÖÐÐÄ.txt"), "配置说明\r\n")
    W(os.path.join(t, "setup.exe"), PE)
    W(os.path.join(t, "install.bat"), "@echo off\r\nexit /b 0\r\n")
    print("[OK] A26-06-garbled-names")

    # ---- A26-07 autorun 指向不存在的文件 ----
    t = tree("A26-07-autorun-missing")
    W(os.path.join(t, "autorun.inf"), AUTORUN_MISSING)
    W(os.path.join(t, "readme.txt"), "autorun 指向不存在的安装器\r\n")
    W(os.path.join(t, "normal-setup.exe"), PE)
    print("[OK] A26-07-autorun-missing")

    # ---- A26-08 installer_media + 深层长路径（MAX_PATH 相关）----
    t = tree("A26-08-deep-longpath")
    deep = os.path.join(t, "a", "b", "c", "d", "e", "f", "g", "h")
    W(os.path.join(deep, "setup.exe"), PE)
    W(os.path.join(t, "install.bat"), "@echo off\r\nexit /b 0\r\n")
    print("[OK] A26-08-deep-longpath")

    print("\nISO 源目录树就绪: %s" % TREES)
    for n in sorted(os.listdir(TREES)):
        cnt = sum(len(f) for _, _, f in os.walk(os.path.join(TREES, n)))
        print("   %-28s %d 个文件" % (n, cnt))


if __name__ == "__main__":
    build_all()
