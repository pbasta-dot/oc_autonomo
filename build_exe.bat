@echo off
setlocal

REM Limpieza
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul

REM Build (modo carpeta para que sea más estable)
pyinstaller ^
  --noconfirm ^
  --clean ^
  --name OC_Autonomo ^
  --onedir ^
  --console ^
  --add-data "templates;templates" ^
  --add-data "data;data" ^
  --add-data "users.json;." ^
  app.py

echo.
echo ✅ Build terminado. Revisa dist\OC_Autonomo\
pause
