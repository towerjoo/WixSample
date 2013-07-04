python gen_wxs.py -v 1.0.0.1
echo "The latest zpst.wxs is generated!"
candle zpst.wxs MyWixUI_InstallDir.wxs MyInstallDirDlg.wxs
:: en-us
light -o zpst.msi -ext WixUIExtension -ext WixUtilExtension -sice:ICE20 -cultures:en-us -loc extra.en.wxl zpst.wixobj MyWixUI_InstallDir.wixobj MyInstallDirDlg.wixobj
python gen_wxs.py -a clean

python gen_wxs.py -v 1.0.0.1 -l 2052
echo "The latest zpst.wxs is generated!"
candle zpst.wxs MyWixUI_InstallDir.wxs MyInstallDirDlg.wxs
:: zh-cn
light -o zpst_zh.msi -ext WixUIExtension -ext WixUtilExtension -sice:ICE20 -cultures:zh-cn -loc extra.zh-cn.wxl zpst.wixobj MyWixUI_InstallDir.wixobj MyInstallDirDlg.wixobj
::light -o zpst.msi -ext WixUIExtension -ext WixUtilExtension -sice:ICE20 -cultures:en,zh-cn -loc extra.zh-cn.wxl -loc extra.en.wxl zpst.wixobj MyWixUI_InstallDir.wixobj MyInstallDirDlg.wixobj
::light -o zpst.msi -ext WixUIExtension -ext WixUtilExtension -sice:ICE20 -cultures:en,zh-cn zpst.wixobj MyWixUI_InstallDir.wixobj MyInstallDirDlg.wixobj
echo "The msi is generated!"
python gen_wxs.py -a clean

torch -t language zpst.msi zpst_zh.msi -out zh.mst

WiSubStg.vbs zpst.msi zh.mst 2052
WiLangId.vbs zpst.msi Package 1033,2052

python gen_wxs.py -a finalclean
