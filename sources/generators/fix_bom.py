# -*- coding: utf-8 -*-
"""把 sources/*.ps1 统一转成 UTF-8 with BOM。
PowerShell 5.1 对无 BOM 的 UTF-8 脚本按 ANSI 解码，会导致中文串与引号错乱（PRD C39 同款坑）。
用法: python sources/fix_bom.py
"""
import glob, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ROOT)
targets = sorted(glob.glob(os.path.join(ROOT, "*.ps1"))) + sorted(glob.glob(os.path.join(BASE, "*.ps1")))
if not targets:
    print("没有找到 .ps1")
for p in targets:
    raw = open(p, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        print("[SKIP] 已有 BOM: %s" % os.path.basename(p))
        continue
    open(p, "wb").write(b"\xef\xbb\xbf" + raw)
    print("[ OK ] 已加 BOM: %s (%d 字节)" % (os.path.basename(p), len(raw)))
