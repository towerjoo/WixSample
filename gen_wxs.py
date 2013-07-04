# coding: utf-8
import os,sys
import uuid

MANUFACTURER = "ZT"
VERSION = "1.0.0.1"
LANG = "1033" #English
#LANG = "2052" #Chinese

ROOT = os.path.abspath(os.path.dirname(__file__))

WXS_TPL = """<?xml version='1.0' encoding='windows-1252'?>
<Wix xmlns='http://schemas.microsoft.com/wix/2006/wi'>
  <Product Name='ZPST' Id='c560d640-86C7-4D14-AEC0-86416A69ABDE' UpgradeCode='c560d640-7349-453F-94F6-BCB5110BA4FD'
    Version="%(version)s" 
    Language='%(language)s' Manufacturer='!(loc.Other_Manufacturer)'>

    <Package Id='*' Keywords='Installer'
      Description="!(loc.Other_PkgDesc)"
      Comments='!(loc.Other_PkgComments)' Manufacturer='!(loc.Other_Manufacturer)'
      InstallerVersion='100' Languages='%(language)s' Compressed='yes' SummaryCodepage='1252' />

    <Media Id='1' Cabinet='Sample.cab' EmbedCab='yes' DiskPrompt="CD-ROM #1" />
    <Property Id='DiskPrompt' Value="ZT's ZPST Installation [1]" />

    <Directory Id='TARGETDIR' Name='SourceDir'>
      <Directory Id='ProgramFilesFolder' Name='PFiles'>
        <Directory Id='ZT' Name='ZT'>
          <Directory Id='INSTALLDIR' Name='ZPST'>

            <Component Id='MainExecutable' Guid='c560d640-83F1-4F22-985B-FDB3C8ABD471'>
              <File Id='ZPSTEXE' Name='zpst.exe' DiskId='1' Source='zpst.exe' KeyPath='yes'>
                <Shortcut Id="startmenuZPST10" Directory="ProgramMenuDir" Name="ZPST" WorkingDirectory='INSTALLDIR' Icon="ZPST.exe" IconIndex="0" Advertise="yes" />
              </File>
            </Component>

            <Component Id="DesktopShortcut" Guid="c560d640-83F1-4F22-985B-FDB3C8ABD499">
               <Condition>INSTALLDESKTOPSHORTCUT</Condition>
               <RegistryValue Id="RegShortcutDesktop" Root="HKCU" Key="SOFTWARE\ZT\ZPST\DesktopShortcut" Name="DesktopSC" Value="1" Type="integer" KeyPath="yes" />
                <Shortcut Id="desktopZPST10" Target="[INSTALLDIR]zpst.exe" Directory="DesktopFolder" Name="ZPST" Icon="ZPST.exe" IconIndex="0" WorkingDirectory="INSTALLDIR" Advertise="no"/>
                <RemoveFolder Id="RemoveShortcutFolder" On="uninstall" />

            </Component>
            

            <Component Id='Help' Guid='c560d640-574D-4A9A-A266-5B5EC2C022A4'>
                <File Id='Help' Name='zpst_help.chm' DiskId='1' Source='resource/help/zpst_help.chm' KeyPath='yes'>
                <Shortcut Id="startmenuManual" Directory="ProgramMenuDir" Name="!(loc.Other_Help)" Advertise="yes" />
              </File>
            </Component>

            %(components)s

          </Directory>
        </Directory>
      </Directory>

      <Directory Id="ProgramMenuFolder" Name="Programs">
        <Directory Id="ProgramMenuDir" Name="ZPST">
          <Component Id="ProgramMenuDir" Guid="c560d640-7E98-44CE-B049-C477CC0A2B00">
            <RemoveFolder Id='ProgramMenuDir' On='uninstall' />
            <RegistryValue Root='HKCU' Key='Software\ZT\ZPST' Type='string' Value='ZPST' KeyPath='yes' />

            <Shortcut Id="UninstallProduct"             
                Name="!(loc.Other_Uninstall)"
                Description="!(loc.Other_Uninstall)"
                Target="[System64Folder]msiexec.exe"
                Arguments="/x [ProductCode]"/>

          </Component>
        </Directory>
      </Directory>

      <Directory Id="DesktopFolder" Name="Desktop" />
    </Directory>

    

    <Feature Id='Complete' Title='ZPST' Description='The complete package.'
      Display='expand' Level='1' ConfigurableDirectory='INSTALLDIR'>
      <Feature Id='MainProgram' Title='Program' Description='The main executable.' Level='1'>
        <ComponentRef Id='MainExecutable' />
        <ComponentRef Id='DesktopShortcut' />
        <ComponentRef Id='ProgramMenuDir' />
        <ComponentRef Id='Help' />
        %(features)s
      </Feature>
    </Feature>



    <Property Id="WIXUI_INSTALLDIR" Value="INSTALLDIR" />
    <Property Id="INSTALLDESKTOPSHORTCUT" Value="1" />
    <Property Id="WIXUI_EXITDIALOGOPTIONALCHECKBOX" Value="1" />
    <UIRef Id="MyWixUI_InstallDir" />
    <UIRef Id="WixUI_ErrorProgressText" />

     <Icon Id="ZPST.exe" SourceFile="zpst.exe" />
     <Property Id="ARPPRODUCTICON" Value="ZPST.exe" />
     <Property Id="ALLUSERS" Value="1" />



    <UI>
        <UIRef Id="MyWixUI_InstallDir" />
    <!-- Skip license dialog -->
    <Publish Dialog="WelcomeDlg"
             Control="Next"
             Event="NewDialog"
             Value="MyInstallDirDlg"
             Order="2">1</Publish>
    <Publish Dialog="MyInstallDirDlg"
             Control="Back"
             Event="NewDialog"
             Value="WelcomeDlg"
             Order="2">1</Publish>
        <Publish Dialog="ExitDialog" 
            Control="Finish" 
            Event="DoAction" 
            Value="LaunchApplication">WIXUI_EXITDIALOGOPTIONALCHECKBOX = 1 and NOT Installed</Publish>
    </UI>
    <Property Id="WIXUI_EXITDIALOGOPTIONALCHECKBOXTEXT" Value="!(loc.Other_LaunchApp)" />

    <Property Id="WixShellExecTarget" Value="[#ZPSTEXE]" />
    <CustomAction Id="LaunchApplication" 
        BinaryKey="WixCA" 
        DllEntry="WixShellExec"
        Impersonate="yes" />

</Product>
</Wix>"""

tpl2 = """<Component Id='%(Id)s' Guid='%(uuid)s'>
                    <File Id='%(Id)s' Name='%(filename)s' DiskId='1' Source='%(path)s' KeyPath='yes'>
                  </File>
                </Component>
"""
tpl3 = """<ComponentRef Id="%(Id)s" />
"""

tpl4 = """<Directory Id="%(Id)s" Name="%(name)s" >
%(cont)s
</Directory>
"""

components = ""
features = ""

files = {}

TARGET = ROOT

def del_old_files(keep_msi=False, excludes=["MyInstallDirDlg.wxs", "MyWixUI_InstallDir.wxs"]):
    file_suffixes = ["wxs", "wixobj", "wixpdb", "msi"]
    if keep_msi:
        file_suffixes.remove("msi")
    for f in os.listdir(TARGET):
        af = os.path.join(TARGET, f)
        if os.path.isdir(af):
            continue
        if f in excludes:
            continue
        for suffix in file_suffixes:
            if f.endswith(suffix):
                os.remove(af)
                break
def final_clean():
    files = ["zpst_zh.msi", "zh.mst"]
    for f in files:
        af = os.path.join(TARGET, f)
        os.remove(af)


def get_rel_dir(af):
    p = os.path.abspath(os.path.dirname(af))
    a = p.split(TARGET)[-1].replace("\\", ".")
    return a[1:] if a.startswith(".") else a


def proc(path, exclude=["MyWixUI_InstallDir.wxs", "MyInstallDirDlg.wxs", ".svn", "zpst.wixobj", "zpst.wixpdb", "zpst.exe", "zpst_help.chm", "gen_installer.bat", "gen_wxs.py", "zpst.msi", "extra.en.wxl", "extra.zh-cn.wxl", "WiSubStg.vbs", "WiLangId.vbs"]):
    for f in os.listdir(path):
        if f in exclude: continue

        af = os.path.join(path, f)
        if os.path.isdir(af):
            proc(af)
        else:
            rel = get_rel_dir(af)
            if rel not in files:
                files[rel] = [f]
            else:
                files[rel].append(f)

import argparse

parser = argparse.ArgumentParser(description='Generate the msi installer')
parser.add_argument('-a', '--action', dest='action', action='store',
                   help='action to do')
parser.add_argument('-v', '--version', dest='version', action='store',
                   help='version of the msi', default=VERSION)
parser.add_argument('-l', '--language', dest='language', action='store',
                   help='language code', default=LANG)

args = parser.parse_args()
if args.action and args.action == "clean":
    del_old_files(True)
    sys.exit(0)
if args.action and args.action == "finalclean":
    final_clean()
    sys.exit(0)

VERSION = args.version
LANG = args.language


del_old_files(True)
proc(TARGET)
i = 0
for key, value in files.iteritems():
    if key == "":
        for item in value:
            i += 1
            data = {
                    "Id" : "Item%d" % i,
                    "uuid" : str(uuid.uuid1()),
                    "path" : item,
                    "filename" : item,
                    }
            components += tpl2 % data
            features += tpl3 % data
    else:
        parts = key.split(".")
        parts.reverse()
        j = 1
        outer = ""
        for p in parts:
            name = p
            if j == 1:
                cont = "REPLACEME"
            else:
                cont = outer
            outer = tpl4 % {"Id": "%s%d" % (name, i), "name" : name, "cont" : cont}
            j += 1
        leader_path = key.replace(".", "/")
        nest_items = ""
        for item in value:
            i += 1
            data = {
                    "Id" : "Item%d" % i,
                    "uuid" : str(uuid.uuid1()),
                    "path" : leader_path + "/" + item,
                    "filename" : item,
                    }
            nest_items += tpl2 % data
            features += tpl3 % data
        components += outer.replace("REPLACEME", nest_items)

TPL = WXS_TPL
final_res = TPL % {
        "components" : components,
        "features" : features,
        "manufacturer" : MANUFACTURER,
        "version" : VERSION,
        "language" : LANG,
        }

fh = open(os.path.join(ROOT, "zpst.wxs"), "w")
fh.write(final_res)
fh.close()


    
