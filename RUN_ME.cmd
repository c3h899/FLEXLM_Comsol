@ECHO OFF
ECHO Summary of COMSOL Licenses in Use
python.exe Query_FlexNet.py --lic COMSOL.lic --users
ECHO.
PAUSE
