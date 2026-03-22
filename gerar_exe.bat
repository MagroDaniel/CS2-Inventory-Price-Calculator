@echo off
title CS2 Inventory Exporter - Instalador
color 0A
echo.
echo  ============================================
echo    CS2 Inventory Exporter - Gerando .EXE
echo  ============================================
echo.

echo [1/3] Instalando dependencias...
python -m pip install requests pyinstaller
if %errorlevel% neq 0 (
    echo.
    echo  ERRO: pip nao encontrado. Instale o Python primeiro.
    echo  python.org/downloads  ^(marque "Add to PATH"^)
    pause
    exit /b 1
)

echo.
echo [2/3] Gerando executavel...
python -m PyInstaller --onefile --windowed --name "CS2_Inventory_Exporter" inventario_cs2_gui.py
if %errorlevel% neq 0 (
    echo.
    echo  ERRO ao gerar o .exe. Veja mensagens acima.
    pause
    exit /b 1
)

echo.
echo [3/3] Pronto!
echo.
echo  O arquivo CS2_Inventory_Exporter.exe esta em:
echo  %cd%\dist\CS2_Inventory_Exporter.exe
echo.
explorer dist
pause
