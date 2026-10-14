# -*- coding: utf-8 -*-
"""
样本自检 v2：用「PE 节表 + 字符串指纹 + 数字签名」三重证据确证每个样本的类型与安装器家族，
并输出机器可读的 sources/sample-index.json 供生成清单。
用法: python sources/verify_samples.py
"""
import json, os, struct, subprocess, sys

ROOT = os.environ.get("ATS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "samples")
OUT_JSON = os.path.join(ROOT, "manifests", "sample-index.json")

PE_EXTS = (".exe", ".dll", ".scr", ".com")
IMG_EXTS = (".iso", ".img")
PKG_EXTS = (".msi", ".msp")

MAGIC = [
    (b"MZ", "PE"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "OLE"),
    (b"%PDF", "PDF"),
    (b"PK\x03\x04", "ZIP"),
    (b"7z\xbc\xaf\x27\x1c", "7Z"),
    (b"Rar!\x1a\x07", "RAR"),
    (b"ITSF", "CHM"),
    (b"\x4c\x00\x00\x00", "LNK"),
]


def pe_sections(data):
    try:
        e = struct.unpack_from("<I", data, 0x3C)[0]
        if data[e:e + 4] != b"PE\0\0":
            return []
        n = struct.unpack_from("<H", data, e + 6)[0]
        opt = struct.unpack_from("<H", data, e + 20)[0]
        so = e + 24 + opt
        return [data[so + i * 40:so + i * 40 + 8].rstrip(b"\0").decode("latin1") for i in range(n)]
    except Exception:
        return []


def family_of(data, sections, name):
    """家族判定：节表优先（比字符串可靠），字符串兜底。"""
    sset = set(sections)
    if ".wixburn" in sset:
        return "WiX Burn bootstrapper"
    if {".itext", ".didata"} & sset or b"Inno Setup" in data:
        return "Inno Setup"
    if ".ndata" in sset or b"Nullsoft" in data:
        return "NSIS"
    if {".fptable", ".didat"} & sset or b"Advanced Installer" in data:
        return "Advanced Installer"
    if b"InstallShield" in data or b"ISSetupStream" in data or b"InstallScript" in data:
        return "InstallShield"
    if b"Squirrel" in data:
        return "Squirrel/Electron"
    if b"Setup Factory" in data:
        return "Setup Factory"
    if b"Wise Installation" in data:
        return "Wise"
    if b"InstallAware" in data:
        return "InstallAware"
    if data.startswith(b"\xd0\xcf\x11\xe0"):
        return "MSI(OLE)"
    # 名称兜底线索（供人工判断，不算确证）
    low = name.lower()
    if any(k in low for k in ("installer", "setup", "install")):
        return "未识别家族(名称含 install/setup)"
    return "未识别家族"


def signature(path):
    """读取内嵌数字签名的主题（离线，仅读证书表，不联网校验时间戳）。"""
    try:
        p = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "(Get-AuthenticodeSignature -LiteralPath '%s').SignerCertificate.Subject" % path],
                           capture_output=True, text=True, timeout=60)
        subj = (p.stdout or "").strip()
        return subj if subj and "Exception" not in subj else ""
    except Exception:
        return ""


def scan():
    items = []
    for dp, _, fns in os.walk(S):
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext not in (PE_EXTS + IMG_EXTS + PKG_EXTS):
                continue
            try:
                size = os.path.getsize(p)
                with open(p, "rb") as f:
                    head = f.read(16)
                    data = head + f.read()
            except OSError:
                continue
            magic = next((n for m, n in MAGIC if data.startswith(m)), "未知")
            if size == 0:
                magic = "空文件"
            sections = pe_sections(data) if data[:2] == b"MZ" else []
            fam = family_of(data, sections, fn) if data[:2] == b"MZ" else (
                "MSI(OLE)" if magic == "OLE" else "-")
            items.append(dict(
                path=os.path.relpath(p, S).replace("\\", "/"),
                group=os.path.relpath(p, S).split(os.sep)[0],
                name=fn, size=size, ext=ext, magic=magic,
                family=fam, sections=sections,
            ))
    return items


def main():
    items = scan()
    print("扫描到 %d 个二进样本\n" % len(items))

    # 签名只对"真实下载的软件"取，合成样本无签名
    real_groups = ("01-", "02-", "03-", "04-", "05-")
    for it in items:
        if it["group"].startswith(real_groups) and it["size"] > 100000:
            it["signer"] = signature(os.path.join(S, it["path"].replace("/", os.sep)))
        else:
            it["signer"] = ""

    print("%-56s %-12s %-28s %10s" % ("样本", "魔数", "安装器家族", "大小"))
    print("-" * 112)
    for it in items:
        sz = ("%.1fMB" % (it["size"] / 1048576)) if it["size"] > 1048576 else ("%.0fKB" % (it["size"] / 1024))
        print("%-56s %-12s %-28s %10s" % (it["path"][-54:], it["magic"], it["family"], sz))

    print("\n===== 真实下载样本的身份核验（数字签名）=====")
    for it in items:
        if it["signer"]:
            cn = it["signer"].split(",")[0]
            print("  %-50s %s" % (it["name"][:48], cn))

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print("\n已写出: %s" % OUT_JSON)

    # 家族分布
    from collections import Counter
    c = Counter(i["family"] for i in items)
    print("\n===== 家族分布 =====")
    for k, v in c.most_common():
        print("  %-34s %d" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
