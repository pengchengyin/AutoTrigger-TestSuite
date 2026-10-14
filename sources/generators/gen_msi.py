# -*- coding: utf-8 -*-
"""
用 WiX v3 生成真实 MSI 样本，覆盖 F4 / F15（S1/S3/S4、1603 反证据、3010 重启、per-user HKCU）。
  -> samples/19-合成安装器(MSI-WiX)
用法: python sources/gen_msi.py
"""
import os, shutil, subprocess, sys, uuid

ROOT = os.environ.get("ATS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "samples")
BUILD = os.path.join(ROOT, "sources", "wix")
PAYLOAD = os.path.join(ROOT, "sources", "payload")
WIX = os.path.join(ROOT, "_toolchain", "wix314")
CANDLE = os.path.join(WIX, "candle.exe")
LIGHT = os.path.join(WIX, "light.exe")
DARK = os.path.join(WIX, "dark.exe")
TORCH = os.path.join(WIX, "torch.exe")
OUTDIR = os.path.join(S, "19-合成安装器(MSI-WiX)")
SENT = r"C:\Users\Public\AT-SENTINEL"


def guid(seed):
    """由种子生成稳定 GUID。"""
    return "{%s}" % str(uuid.uuid5(uuid.NAMESPACE_URL, "at-testsuite/" + seed)).upper()


WXS = r"""<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="{name}" Language="1033" Version="{version}"
           Manufacturer="AT-TestSuite" UpgradeCode="{upgrade}">
    <Package Id="*" InstallerVersion="500" Compressed="yes" InstallScope="{scope}"
             InstallPrivileges="{priv}" Description="{name}" Comments="AT synthetic MSI sample" />
    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." AllowSameVersionUpgrades="yes" />
    <MediaTemplate EmbedCab="yes" />

    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="{rootdir}">
        <Directory Id="INSTALLFOLDER" Name="{foldername}" />
      </Directory>
    </Directory>

    <DirectoryRef Id="INSTALLFOLDER">
{components}
      <Component Id="cmpSentinel" Guid="{sentguid}">
        <RegistryKey Root="{reghive}" Key="Software\AT-TestSuite\{regname}">
          <RegistryValue Type="string" Name="Installed" Value="1" KeyPath="yes" />
          <RegistryValue Type="string" Name="Version" Value="{version}" />
          <RegistryValue Type="string" Name="InstallLocation" Value="[INSTALLFOLDER]" />
        </RegistryKey>
      </Component>
    </DirectoryRef>

    <Feature Id="MainFeature" Title="AT Synthetic MSI" Level="1" Display="expand">
      <ComponentRef Id="cmpSentinel" />
{featurerefs}
    </Feature>

    <Property Id="ARPPRODUCTICON" Value="app.exe" />
{extra_props}
{extra_ca}
    <InstallExecuteSequence>
{extra_seq}
    </InstallExecuteSequence>

    <UIRef Id="WixUI_Minimal" />
  </Product>
</Wix>
"""


def build(spec, name, wxs_text, out_msi):
    src = os.path.join(BUILD, name + ".wxs")
    os.makedirs(BUILD, exist_ok=True)
    with open(src, "w", encoding="utf-8") as f:
        f.write(wxs_text)
    obj = os.path.join(BUILD, name + ".wixobj")
    p1 = subprocess.run([CANDLE, "-nologo", "-arch", "x64", "-out", obj, src],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p1.returncode != 0 or not os.path.exists(obj):
        return ("FAIL-candle", (p1.stdout or "") + (p1.stderr or ""))
    p2 = subprocess.run([LIGHT, "-nologo", "-sval", "-ext", "WixUIExtension",
                         "-cultures:en-us", "-out", out_msi, obj],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.exists(out_msi):
        return ("FAIL-light", (p2.stdout or "") + (p2.stderr or ""))
    return ("OK", os.path.getsize(out_msi))


def make(seed, name, foldername, version="1.0.0.0", scope="perMachine", priv="elevated",
         rootdir="ProgramFiles64Folder", reghive="HKLM", files=None,
         extra_props="", extra_ca="", extra_seq="", regname=None):
    files = files or ["app.exe", "core.dll", "resources.dat", "readme.txt"]
    comps, refs = [], []
    for i, fn in enumerate(files):
        cid = "cmp%d" % i
        comps.append(
            '      <Component Id="%s" Guid="%s">\n'
            '        <File Id="fil%d" Source="%s" KeyPath="yes" />\n'
            '      </Component>' % (cid, guid(seed + "/" + cid), i, os.path.join(PAYLOAD, fn)))
        refs.append('      <ComponentRef Id="%s" />' % cid)
    return WXS.format(
        name=name, version=version, upgrade=guid(seed + "/upgrade"),
        scope=scope, priv=priv, rootdir=rootdir, foldername=foldername,
        components="\n".join(comps), featurerefs="\n".join(refs),
        sentguid=guid(seed + "/sentinel"), reghive=reghive,
        regname=regname or seed, extra_props=extra_props, extra_ca=extra_ca,
        extra_seq=extra_seq)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    ok = fail = 0
    specs = []

    # ---- 01 标准 per-machine 安装成功（S1 + S3 + S4）----
    specs.append(("MSI-01-标准安装成功", make("MSI01", "AT Synthetic MSI 01", "ATSynthMsi01")))

    # ---- 02 安装致命错误 1603（N1 反证据 + A34 日志保留）----
    specs.append(("MSI-02-安装致命错误1603",
                  make("MSI02", "AT Synthetic MSI 02 Fail1603", "ATSynthMsi02",
                       extra_ca='    <CustomAction Id="FailInstall" Error="Simulated fatal error: installation failed (1603)" />',
                       extra_seq='      <Custom Action="FailInstall" After="InstallFiles">NOT Installed</Custom>')))

    # ---- 03 需重启（3010）----
    specs.append(("MSI-03-需重启3010",
                  make("MSI03", "AT Synthetic MSI 03 Reboot", "ATSynthMsi03",
                       extra_props='    <Property Id="REBOOT" Value="Force" />',
                       extra_seq='      <ScheduleReboot After="InstallFinalize">NOT Installed</ScheduleReboot>')))

    # ---- 04 per-user 安装（只写 HKCU，验证 A29 ④）----
    specs.append(("MSI-04-per-user安装",
                  make("MSI04", "AT Synthetic MSI 04 PerUser", "ATSynthMsi04",
                       scope="perUser", priv="limited",
                       rootdir="LocalAppDataFolder", reghive="HKCU")))

    # ---- 05 多文件较长安装 ----
    many = ["app.exe"] + ["bigpayload.bin"] + ["core.dll", "resources.dat", "readme.txt"]
    specs.append(("MSI-05-多文件较长安装",
                  make("MSI05", "AT Synthetic MSI 05 Long", "ATSynthMsi05", files=many)))

    # ---- 06 升级链 V1 / V2 ----
    specs.append(("MSI-06-升级覆盖V1",
                  make("MSI06", "AT Synthetic MSI 06 Upgrade", "ATSynthMsi06", version="1.0.0.0")))
    specs.append(("MSI-06-升级覆盖V2",
                  make("MSI06", "AT Synthetic MSI 06 Upgrade", "ATSynthMsi06", version="2.0.0.0")))

    # ---- 07 非 MSI 内容但扩展名为 .msi ----
    specs.append(("MSI-07-无效MSI-纯文本内容", "PLAINTEXT"))

    for name, wxs in specs:
        out = os.path.join(OUTDIR, name + ".msi")
        if wxs == "PLAINTEXT":
            with open(out, "w", encoding="utf-8") as f:
                f.write("这不是一个真正的 MSI 安装包，只是一个文本文件。\nThis is not a valid MSI package.\n")
            ok += 1
            print("[OK]   %-40s %8.1fKB (伪 MSI)" % (name, os.path.getsize(out) / 1024))
            continue
        st, info = build(name, name, wxs, out)
        if st == "OK":
            ok += 1
            print("[OK]   %-40s %8.1fKB" % (name, info / 1024))
        else:
            fail += 1
            print("[FAIL] %-40s %s\n%s" % (name, st, info[-1200:]))

    # ---- 08 损坏的 MSI：取 MSI-01 并截断 ----
    good = os.path.join(OUTDIR, "MSI-01-标准安装成功.msi")
    if os.path.exists(good):
        data = open(good, "rb").read()
        with open(os.path.join(OUTDIR, "MSI-08-损坏的MSI.msi"), "wb") as f:
            f.write(data[:len(data) // 3])
        print("[OK]   %-40s %8.1fKB (截断至 1/3)" % ("MSI-08-损坏的MSI", os.path.getsize(
            os.path.join(OUTDIR, "MSI-08-损坏的MSI.msi")) / 1024))

    print("\nMSI: 成功 %d / 失败 %d" % (ok, fail))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    if not os.path.exists(CANDLE):
        print("缺少 candle.exe")
        sys.exit(1)
    sys.exit(main())
