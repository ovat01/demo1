@echo off
echo "Creando el ejecutable optimizado..."

REM Comando de PyInstaller sin --hidden-import=ttkthemes
pyinstaller --windowed --add-data "assets;assets" --add-data "tools;tools" --name "ReimpresorBoletas" src/main.py

echo "Build finalizado. Revisa la carpeta 'dist'."
pause
