# -*- coding: utf-8 -*-
"""
生成数据类测试样本：
 - 09 类型识别与伪装（文件头 vs 扩展名）
 - 08 文档类（PDF / DOCX / XLSX / RTF / PPTX / 伪 OLE）
 - 14 跳过与兜底（空文件、损坏包、加密包、zip 炸弹、嵌套包）
 - 10 入口分层与黑名单测试包（目录版 + 压缩包版，对应 A25 / F17）
 - 15 批量与嵌套
用法: python sources/gen_data.py
"""
import os, io, random, shutil, struct, subprocess, sys, zipfile, zlib

ROOT = os.environ.get("ATS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "samples")
TRAP = os.path.join(ROOT, "_trap")
SEVENZ = r"D:\software\7-Zip\7z.exe"
random.seed(20260212)


def d(*p):
    path = os.path.join(S, *p)
    os.makedirs(path, exist_ok=True)
    return path


def w(path, data, mode="wb"):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
        if mode == "w":
            mode = "wb"
    with open(path, mode) as f:
        f.write(data)
    return path


def cp(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return dst


# 拿一个真实的 PE 当"正版载荷"
def a_real_pe():
    for c in [os.path.join(TRAP, "install.bat.exe")]:
        if os.path.exists(c):
            return c
    raise SystemExit("请先运行 gen_csharp.py")


# ============================================================ 09 类型识别与伪装
def gen_type_disguise():
    dd = d("09-类型识别与伪装")
    pe = a_real_pe()
    pe_bytes = open(pe, "rb").read()

    # 扩展名说 exe，实际是 PDF
    w(os.path.join(dd, "实际是PDF的exe.exe"), b"%PDF-1.7\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n")
    # 扩展名说 exe，实际是 ZIP
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("inner.txt", "this is really a zip archive\n")
    w(os.path.join(dd, "实际是ZIP的exe.exe"), buf.getvalue())
    # 扩展名说 exe，实际是纯文本
    w(os.path.join(dd, "实际是文本的exe.exe"), "这其实是一个纯文本文件，不是可执行文件。\n")
    # 扩展名说 txt，实际是 PE => extension_disguised: true（A5）
    w(os.path.join(dd, "实际是PE的txt.txt"), pe_bytes)
    # 扩展名说 docx，实际是 PE
    w(os.path.join(dd, "实际是PE的docx.docx"), pe_bytes)
    # 扩展名说 jpg，实际是 PE
    w(os.path.join(dd, "实际是PE的jpg.jpg"), pe_bytes)
    # 只有 MZ 头、不是有效 PE
    w(os.path.join(dd, "MZ头但非PE.exe"), b"MZ" + bytes(random.getrandbits(8) for _ in range(2048)))
    # OLE 头但非 MSI（扩展名 .msi）
    w(os.path.join(dd, "OLE头伪msi.msi"),
      bytes([0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1]) + bytes(random.getrandbits(8) for _ in range(4096)))
    # LNK 头（4C 00 00 00）但是垃圾数据
    w(os.path.join(dd, "LNK头伪lnk.lnk"),
      b"\x4C\x00\x00\x00" + bytes(random.getrandbits(8) for _ in range(512)))
    # 完全未知的高熵数据
    w(os.path.join(dd, "随机高熵数据.xyz"), bytes(random.getrandbits(8) for _ in range(8192)))
    # 极小的合法 PE 之外的：DOS 头 + 垃圾
    w(os.path.join(dd, "ELF头文件.so"), b"\x7fELF\x02\x01\x01\x00" + bytes(248))
    # Mach-O 头
    w(os.path.join(dd, "MachO头文件.dylib"), b"\xCF\xFA\xED\xFE" + bytes(248))
    print("[OK] 09-类型识别与伪装: %d 个" % len(os.listdir(dd)))


# ============================================================ 08 文档类
MIN_PDF = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]/Contents 4 0 R>>endobj
4 0 obj<</Length 60>>stream
BT /F1 24 Tf 72 720 Td (AT Test Document) Tj ET
endstream
endobj
trailer<</Root 1 0 R>>
%%EOF
"""


def gen_docs():
    dd = d("08-文档类")
    w(os.path.join(dd, "01-有效文档.pdf"), MIN_PDF)
    # 真 DOCX（OPC/ZIP 结构）
    with zipfile.ZipFile(os.path.join(dd, "02-Word文档.docx"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr("word/document.xml",
                   '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                   '<w:body><w:p><w:r><w:t>AT Test Document - 宏触发测试样本</w:t></w:r></w:p></w:body></w:document>')
    # 真 XLSX
    with zipfile.ZipFile(os.path.join(dd, "03-Excel表格.xlsx"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr("xl/workbook.xml", '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"/>')
    # RTF
    w(os.path.join(dd, "04-文档.rtf"), r"{\rtf1\ansi\deff0 {\fonttbl{\f0 Arial;}}\f0\fs24 AT Test RTF\par}")
    # 伪 OLE 的 .doc（老格式，触发关联程序）
    w(os.path.join(dd, "05-老格式.doc"),
      bytes([0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1]) + bytes(2048))
    # PPTX
    with zipfile.ZipFile(os.path.join(dd, "06-幻灯片.pptx"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr("ppt/presentation.xml", '<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>')
    # 宏文档（.docm）
    with zipfile.ZipFile(os.path.join(dd, "07-含宏文档.docm"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr("word/vbaProject.bin", b"\xd0\xcf\x11\xe0" + bytes(1024))
    # 无宿主关联的类型（用于 skipped: no_host_app）
    w(os.path.join(dd, "08-无宿主扩展名.atdoc"), b"ATDOC\x00" + bytes(64))
    print("[OK] 08-文档类: %d 个" % len(os.listdir(dd)))


# ============================================================ 14 跳过与兜底
def gen_skip_fallback():
    dd = d("14-跳过与兜底")
    pe = a_real_pe()
    # 空文件（0 字节）=> skipped: empty_file
    w(os.path.join(dd, "01-空文件.exe"), b"")
    w(os.path.join(dd, "02-空文件.dat"), b"")
    # 1 字节文件
    w(os.path.join(dd, "03-单字节文件.bin"), b"\x00")
    # 损坏压缩包
    w(os.path.join(dd, "04-损坏的zip.zip"), b"PK\x03\x04" + bytes(random.getrandbits(8) for _ in range(1024)))
    w(os.path.join(dd, "05-损坏的7z.7z"), b"7z\xbc\xaf\x27\x1c" + bytes(random.getrandbits(8) for _ in range(1024)))
    # 截断的真实压缩包（取一个真 zip 的前 40%）
    src = os.path.join(S, "06-压缩包", "nssm-2.24.zip")
    if os.path.exists(src):
        data = open(src, "rb").read()
        w(os.path.join(dd, "06-截断的zip.zip"), data[:int(len(data) * 0.4)])
    # 加密的 zip
    tmp = os.path.join(ROOT, "_tmp", "enc_src")
    os.makedirs(tmp, exist_ok=True)
    w(os.path.join(tmp, "secret.txt"), "AT encrypted payload\n")
    subprocess.run([SEVENZ, "a", "-tzip", "-pATtest123", os.path.join(dd, "07-加密zip.zip"), os.path.join(tmp, "secret.txt")],
                   capture_output=True)
    # 加密的 7z（含文件名加密）
    subprocess.run([SEVENZ, "a", "-t7z", "-pATtest123", "-mhe=on", os.path.join(dd, "08-加密7z-文件名加密.7z"),
                    os.path.join(tmp, "secret.txt")], capture_output=True)
    # 未知扩展名但 MZ 头 => 按 PE 执行
    cp(pe, os.path.join(dd, "09-未知扩展名但MZ头.qwerty"))
    print("[OK] 14-跳过与兜底（第一段）: %d 个" % len(os.listdir(dd)))


def gen_zipbomb():
    """高压缩比样本：解压后约 2.2GB，超过默认 2GB 上限 => extract_size_exceeded。
    注意：若被测工具未按 F17.1 预检，会真的写出 2GB 数据；请确认磁盘余量。"""
    dd = d("14-跳过与兜底")
    out = os.path.join(dd, "10-zip炸弹-解压超2G.zip")
    if os.path.exists(out):
        print("[SKIP] zip 炸弹已存在")
        return
    chunk = b"\0" * (8 * 1024 * 1024)          # 8MB 零块
    total = 2200 * 1024 * 1024                 # 2.2GB 未压缩
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        with z.open("bomb.bin", "w", force_zip64=True) as f:
            written = 0
            while written < total:
                f.write(chunk)
                written += len(chunk)
    print("[OK] zip 炸弹: %.1fMB（解压后 %.1fGB）" % (os.path.getsize(out) / 1048576.0, total / 1073741824.0))


def gen_nested():
    """多层嵌套压缩包（递归深度限制，默认 3 层）。"""
    tmp = os.path.join(ROOT, "_tmp", "nested")
    if os.path.isdir(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    # 最内层：真正会被触发的安装器
    inner_exe = os.path.join(tmp, "level4-installer.exe")
    cp(a_real_pe(), inner_exe)
    w(os.path.join(tmp, "level4-payload.txt"), "deepest payload\n")
    l3 = os.path.join(tmp, "level3.7z")
    subprocess.run([SEVENZ, "a", "-t7z", l3, inner_exe, os.path.join(tmp, "level4-payload.txt")], capture_output=True)
    l2 = os.path.join(tmp, "level2.zip")
    subprocess.run([SEVENZ, "a", "-tzip", l2, l3], capture_output=True)
    l1 = os.path.join(tmp, "level1.7z")
    subprocess.run([SEVENZ, "a", "-t7z", l1, l2], capture_output=True)
    dd = d("15-批量与嵌套")
    cp(l1, os.path.join(dd, "01-三层嵌套.7z"))
    # 两层（在深度限制内，应能触发最内层）
    dd2 = d("06-压缩包", "嵌套包")
    cp(l2, os.path.join(dd2, "02-两层嵌套.zip"))
    cp(l3, os.path.join(dd2, "01-一层嵌套.7z"))
    print("[OK] 嵌套压缩包: 1/2/3 层各一份")


# ============================================================ 10 入口分层 A25 / F17
def trap(name, dst_dir):
    src = os.path.join(TRAP, name)
    if not os.path.exists(src):
        print("  缺少陷阱样本: " + name)
        return None
    return cp(src, os.path.join(dst_dir, name))


def gen_pkg_a25_01():
    """A25 ① ② ④：install.bat + setup.exe + unins000.exe + 数十 DLL 的规范测试包。"""
    dd = d("10-入口分层与黑名单", "A25-01-规范包-含黑名单")
    w(os.path.join(dd, "安装说明.txt"),
      "安装说明\r\n========\r\n双击 install.bat 开始安装。\r\n若需要静默安装，请运行 setup.exe /S\r\n")
    w(os.path.join(dd, "install.bat"),
      "@echo off\r\n"
      "echo [install.bat] 正在安装 A25-01 测试包...\r\n"
      "if not exist \"C:\\Users\\Public\\AT-SENTINEL\" mkdir \"C:\\Users\\Public\\AT-SENTINEL\"\r\n"
      "echo ENTRY-install.bat >> \"C:\\Users\\Public\\AT-SENTINEL\\ran.log\"\r\n"
      "if not exist \"%ProgramFiles%\\ATPackageA2501\" mkdir \"%ProgramFiles%\\ATPackageA2501\"\r\n"
      "echo installed > \"%ProgramFiles%\\ATPackageA2501\\installed.txt\"\r\n"
      "reg add \"HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ATPackageA2501\" /v DisplayName /t REG_SZ /d \"AT Package A25-01\" /f >nul\r\n"
      "reg add \"HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ATPackageA2501\" /v DisplayVersion /t REG_SZ /d \"1.0.0\" /f >nul\r\n"
      "reg add \"HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ATPackageA2501\" /v InstallLocation /t REG_SZ /d \"%ProgramFiles%\\ATPackageA2501\" /f >nul\r\n"
      "echo [install.bat] 安装完成\r\n"
      "exit /b 0\r\n")
    # P2 标准安装器（用真实 NSIS/Inno 合成件，若已生成则复制，否则用陷阱）
    for n in ["setup.exe", "setup_x64.exe", "setup_x86.exe"]:
        src_inno = os.path.join(S, "17-合成安装器(Inno)", "INNO-01-静默安装成功.exe")
        src_nsis = os.path.join(S, "18-合成安装器(NSIS)", "NSIS-01-静默安装成功.exe")
        if os.path.exists(src_nsis):
            cp(src_nsis, os.path.join(dd, n))
        else:
            trap("install.bat.exe", dd)
            os.replace(os.path.join(dd, "install.bat.exe"), os.path.join(dd, n))
    # P3 前置依赖
    trap("install.bat.exe", dd)
    os.replace(os.path.join(dd, "install.bat.exe"), os.path.join(dd, "vcredist_x64.exe"))
    # P4 主程序
    trap("install.bat.exe", dd)
    os.replace(os.path.join(dd, "install.bat.exe"), os.path.join(dd, "MyApp.exe"))
    # 黑名单（陷阱：被执行就留铁证）
    for n in ["unins000.exe", "卸载.exe", "uninstall.exe", "update.exe", "updater.exe",
              "checkupdate.exe", "crashpad_handler.exe", "crashreporter.exe", "repair.exe",
              "debug-helper.exe", "modify.exe"]:
        trap(n, dd)
    # 数十个 DLL（噪音，验证不被盲目全量执行）
    for i in range(40):
        w(os.path.join(dd, "runtime", "lib%02d.dll" % i),
          b"MZ" + bytes(random.getrandbits(8) for _ in range(512)))
    os.makedirs(os.path.join(dd, "sub", "deep"), exist_ok=True)
    trap("install.bat.exe", os.path.join(dd, "sub", "deep"))
    os.replace(os.path.join(dd, "sub", "deep", "install.bat.exe"),
               os.path.join(dd, "sub", "deep", "tool-p5.exe"))
    # 黑名单文档类
    w(os.path.join(dd, "manual.pdf"), MIN_PDF)
    w(os.path.join(dd, "help.chm"), b"ITSF\x03\x00\x00\x00" + bytes(256))
    w(os.path.join(dd, "readme.txt"), "AT A25-01 test package\n")
    print("[OK] A25-01-规范包-含黑名单")


def gen_pkg_a25_02():
    """A25 ⑥：readme 指向不存在的文件 => 不得产生任何执行动作。"""
    dd = d("10-入口分层与黑名单", "A25-02-readme指向不存在文件")
    w(os.path.join(dd, "安装说明.txt"),
      "安装说明\r\n========\r\n请双击 notexist-installer.exe 开始安装（该文件其实并不存在）。\r\n")
    trap("install.bat.exe", dd)
    os.replace(os.path.join(dd, "install.bat.exe"), os.path.join(dd, "unrelated.exe"))
    print("[OK] A25-02-readme指向不存在文件")


def gen_pkg_a25_03():
    """A25 ⑤：setup_x64.exe 与 setup_x86.exe 并存 => 优先匹配当前架构。"""
    dd = d("10-入口分层与黑名单", "A25-03-架构优先")
    for name, tag in [("setup_x64.exe", "ARCH-x64"), ("setup_x86.exe", "ARCH-x86")]:
        p = trap("install.bat.exe", dd)
        os.replace(p, os.path.join(dd, name))
    w(os.path.join(dd, "install.bat"),
      "@echo off\r\n"
      "if not exist \"C:\\Users\\Public\\AT-SENTINEL\" mkdir \"C:\\Users\\Public\\AT-SENTINEL\"\r\n"
      "echo ARCH-CHOSEN-%%PROCESSOR_ARCHITECTURE%% >> \"C:\\Users\\Public\\AT-SENTINEL\\ran.log\"\r\n"
      "if not exist \"%ProgramFiles%\\ATArchA2503\" mkdir \"%ProgramFiles%\\ATArchA2503\"\r\n"
      "reg add \"HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ATArchA2503\" /v DisplayName /t REG_SZ /d \"AT Arch A25-03\" /f >nul\r\n"
      "exit /b 0\r\n")
    print("[OK] A25-03-架构优先")


def gen_pkg_a25_06():
    """A25 ③：阶段 1 全部失败 => 回退到 P5 兜底（fallback_to_brute）。"""
    dd = d("10-入口分层与黑名单", "A25-06-阶段2兜底")
    w(os.path.join(dd, "安装说明.txt"), "安装说明\r\n========\r\n运行 install.bat\r\n")
    w(os.path.join(dd, "install.bat"),
      "@echo off\r\necho install.bat FAILED\r\nexit /b 1\r\n")
    for name in ["setup.exe", "vcredist_x64.exe", "MyApp.exe", "install-helper.exe"]:
        w(os.path.join(dd, name), b"MZ" + bytes(random.getrandbits(8) for _ in range(512)))
    deep = os.path.join(dd, "deep", "tools", "extra")
    os.makedirs(deep, exist_ok=True)
    cp(a_real_pe(), os.path.join(deep, "runtime-helper.exe"))
    print("[OK] A25-06-阶段2兜底")


def gen_pkg_zip_versions():
    """A25 ④：压缩包场景先 7z l 列清单再解压。"""
    src = os.path.join(S, "10-入口分层与黑名单", "A25-01-规范包-含黑名单")
    if not os.path.isdir(src):
        return
    out_dir = d("10-入口分层与黑名单")
    for fmt, ext in [("-tzip", "zip"), ("-t7z", "7z")]:
        dst = os.path.join(out_dir, "A25-04-规范包压缩版." + ext)
        if os.path.exists(dst):
            os.remove(dst)
        subprocess.run([SEVENZ, "a", fmt, dst, os.path.join(src, "*")], capture_output=True)
    print("[OK] A25-04 压缩包版（zip / 7z）")


# ============================================================ 15 批量 A6
def gen_batch50():
    dd = d("15-批量与嵌套", "A6-批量50文件")
    kinds = ["exe", "dll", "txt", "pdf", "zip", "bat", "ps1", "vbs", "js", "bin"]
    for i in range(50):
        ext = kinds[i % len(kinds)]
        p = os.path.join(dd, "case%02d.%s" % (i + 1, ext))
        if ext == "exe":
            cp(a_real_pe(), p)
        elif ext == "pdf":
            w(p, MIN_PDF)
        elif ext == "zip":
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("a.txt", "batch %d" % i)
        elif ext == "bat":
            w(p, "@echo off\r\necho batch %d\r\n" % i)
        elif ext == "ps1":
            w(p, "Write-Host 'batch %d'\r\n" % i)
        elif ext == "vbs":
            w(p, "WScript.Echo \"batch %d\"\r\n" % i)
        elif ext == "js":
            w(p, "WScript.Echo('batch %d');\r\n" % i)
        else:
            w(p, bytes(random.getrandbits(8) for _ in range(256)))
    print("[OK] A6-批量50文件")


# ============================================================ 07 脚本与快捷方式
def gen_scripts():
    dd = d("07-脚本与快捷方式")
    sent = 'C:\\Users\\Public\\AT-SENTINEL'
    w(os.path.join(dd, "01-批处理.bat"),
      "@echo off\r\nif not exist \"%s\" mkdir \"%s\"\r\necho SCRIPT-bat >> \"%s\\ran.log\"\r\necho bat script executed\r\n"
      % (sent, sent, sent))
    w(os.path.join(dd, "02-命令脚本.cmd"),
      "@echo off\r\nif not exist \"%s\" mkdir \"%s\"\r\necho SCRIPT-cmd >> \"%s\\ran.log\"\r\n" % (sent, sent, sent))
    w(os.path.join(dd, "03-PowerShell.ps1"),
      "$d='%s'\r\nif(!(Test-Path $d)){New-Item -ItemType Directory -Path $d | Out-Null}\r\n"
      "Add-Content -Path (Join-Path $d 'ran.log') -Value 'SCRIPT-ps1'\r\nWrite-Host 'ps1 executed'\r\n" % sent)
    w(os.path.join(dd, "04-VBScript.vbs"),
      'Set fso = CreateObject("Scripting.FileSystemObject")\r\n'
      'If Not fso.FolderExists("%s") Then fso.CreateFolder("%s")\r\n'
      'Set f = fso.OpenTextFile("%s\\ran.log", 8, True)\r\nf.WriteLine "SCRIPT-vbs"\r\nf.Close\r\n'
      'WScript.Echo "vbs executed"\r\n' % (sent, sent, sent))
    w(os.path.join(dd, "05-JScript.js"),
      'var fso = new ActiveXObject("Scripting.FileSystemObject");\r\n'
      'if (!fso.FolderExists("%s")) fso.CreateFolder("%s");\r\n'
      'var f = fso.OpenTextFile("%s\\\\ran.log", 8, true); f.WriteLine("SCRIPT-js"); f.Close();\r\n'
      'WScript.Echo("js executed");\r\n' % (sent, sent, sent))
    w(os.path.join(dd, "06-WSF脚本.wsf"),
      '<?xml version="1.0"?>\r\n<job><script language="VBScript">\r\n'
      'Set fso = CreateObject("Scripting.FileSystemObject")\r\n'
      'Set f = fso.OpenTextFile("%s\\ran.log", 8, True)\r\nf.WriteLine "SCRIPT-wsf"\r\nf.Close\r\n'
      '</script></job>\r\n' % sent)
    # 普通 JS 文本（无 WScript/ActiveXObject）=> F2 细则：无法判定时按 Windows Script 处理
    w(os.path.join(dd, "07-普通JS文本.js"), "function add(a, b) { return a + b; }\nconsole.log(add(1, 2));\n")
    # 带 BOM 的 UTF-16LE 脚本（编码容错）
    with open(os.path.join(dd, "08-UTF16LE批处理.bat"), "wb") as f:
        f.write(b"\xff\xfe" + ("@echo off\r\necho SCRIPT-utf16 >> \"%s\\ran.log\"\r\n" % sent).encode("utf-16-le"))
    print("[OK] 07-脚本与快捷方式（除 lnk/dll）")


def gen_dll():
    """用 csc 编译一个带导出元数据的 DLL（rundll32 触发用）。"""
    dd = d("07-脚本与快捷方式")
    out = os.path.join(dd, "10-导出函数库.dll")
    if os.path.exists(out):
        return
    cs = os.path.join(ROOT, "sources", "csharp", "dll.cs")
    with open(cs, "w", encoding="utf-8-sig") as f:
        f.write(r"""
using System;
using System.Runtime.InteropServices;
public class ATExports {
    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    static extern int MessageBoxW(IntPtr h, string t, string c, uint type);
    [DllExportLike] public static void ATRunDll() { }
    public static void Entry1() { }
    public static void Entry2() { }
    public static void Entry3() { }
    public static void Main() { }
}
public class DllExportLikeAttribute : Attribute { }
""")
    subprocess.run([r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe", "/nologo",
                    "/target:library", "/out:" + out, cs], capture_output=True)
    # 另附一个真实的、确实带原生导出表的 DLL（7-Zip 的 7z.dll）
    src = r"D:\software\7-Zip\7z.dll"
    if os.path.exists(src):
        cp(src, os.path.join(dd, "11-原生导出表(7z).dll"))
    print("[OK] 07-DLL 样本")


if __name__ == "__main__":
    gen_type_disguise()
    gen_docs()
    gen_skip_fallback()
    gen_nested()
    gen_batch50()
    gen_scripts()
    gen_dll()
    gen_pkg_a25_01()
    gen_pkg_a25_02()
    gen_pkg_a25_03()
    gen_pkg_a25_06()
    gen_pkg_zip_versions()
    gen_zipbomb()
    print("\n数据类样本生成完毕。")
