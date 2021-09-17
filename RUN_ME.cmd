@ECHO OFF
ECHO Summary of COMSOL Licenses in Use
ECHO.
python.exe Query_COMSOL.py COMSOL.lic --users
ECHO.
PAUSE
