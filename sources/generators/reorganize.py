# -*- coding: utf-8 -*-
"""
按真实安装器家族重组样本目录，并把探测结果固化下来。
用法: python sources/reorganize.py
"""
import os, shutil, zipfile, sys

ROOT = os.environ.get("ATS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "samples")
CAND = os.path.join(ROOT, "_tmp", "cand")

MOVES = [
    # 源, 目标目录
    (os.path.join(S, "02-NSIS", "audacity-win-3.7.1-64bit.exe"), "01-Inno Setup"),
    (os.path.join(CAND, "Notepad3-Setup.exe"),                   "01-Inno Setup"),
    (os.path.join(CAND, "Recuva.exe"),                           "02-NSIS"),
    (os.path.join(CAND, "Defraggler.exe"),                       "02-NSIS"),
    (os.path.join(CAND, "TeraCopy.exe"),                         "05-其它厂商安装器"),
    (os.path.join(CAND, "VeraCrypt.exe"),                        "05-其它厂商安装器"),
    (os.path.join(CAND, "ZoomInstallerFull.exe"),                "05-其它厂商安装器"),
]


def main():
    os.makedirs(os.path.join(S, "05-其它厂商安装器"), exist_ok=True)

    # 1. 移动真实样本
    for src, dstdir in MOVES:
        if not os.path.exists(src):
            print("[跳过] 源不存在: %s" % os.path.basename(src))
            continue
        dst = os.path.join(S, dstdir, os.path.basename(src))
        if os.path.abspath(src) == os.path.abspath(dst):
            continue
        shutil.move(src, dst)
        print("[移动] %-30s -> %s" % (os.path.basename(src), dstdir))

    # 2. MobaXterm：zip 留在压缩包组，同时把里面的 MSI 解出来放进 MSI 组
    mobazip = os.path.join(S, "05-InstallShield", "MobaXterm_Installer.zip")
    if os.path.exists(mobazip):
        dstzip = os.path.join(S, "06-压缩包", "MobaXterm_Installer.zip")
        shutil.move(mobazip, dstzip)
        print("[移动] MobaXterm_Installer.zip -> 06-压缩包")
        with zipfile.ZipFile(dstzip) as z:
            for n in z.namelist():
                if n.lower().endswith(".msi"):
                    out = os.path.join(S, "03-MSI", os.path.basename(n))
                    with z.open(n) as fsrc, open(out, "wb") as fdst:
                        shutil.copyfileobj(fsrc, fdst)
                    print("[解出] %s -> 03-MSI" % os.path.basename(n))

    # 3. 删除空目录与不再需要的候选
    old = os.path.join(S, "05-InstallShield")
    if os.path.isdir(old):
        shutil.rmtree(old, ignore_errors=True)
        print("[删除] 05-InstallShield（无真正 InstallShield 样本，已由 05-其它厂商安装器 取代）")
    adobe = os.path.join(CAND, "AdbeRdr11000_zh_CN.exe")
    if os.path.exists(adobe):
        os.remove(adobe)
        print("[删除] AdbeRdr11000_zh_CN.exe（体积大且家族不可辨识，Zoom 已覆盖该场景）")
    for j in ("innosetup.nupkg.ok", "nsis.nupkg.ok"):
        p = os.path.join(ROOT, "_toolchain", "choco", j)
        if os.path.exists(p):
            os.remove(p)

    # 4. 汇总
    print("\n===== 重组后的样本组 =====")
    for d in sorted(os.listdir(S)):
        p = os.path.join(S, d)
        if not os.path.isdir(p):
            continue
        n = sum(len(f) for _, _, f in os.walk(p))
        sz = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(p) for f in fs)
        print("  %-30s %4d 文件  %8.2f MB" % (d, n, sz / 1048576))
    return 0


if __name__ == "__main__":
    sys.exit(main())
