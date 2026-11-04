@echo off
cd /d "%~dp0"
:menu
cls
echo ==========================================
echo   CLASIFICADOR DE MATERIALES - OPENCV
echo ==========================================
echo.
echo   1. Probar con la camara
echo   2. Probar con una imagen de ejemplo
echo   3. Medir la precision del modelo
echo   4. Salir
echo.
set /p opcion=Elegi una opcion y presiona Enter: 

if "%opcion%"=="1" goto camara
if "%opcion%"=="2" goto imagen
if "%opcion%"=="3" goto precision
if "%opcion%"=="4" exit
goto menu

:camara
echo.
echo Abriendo la camara... mostra un objeto y presiona Q para salir.
python clasificador_opencv.py
pause
goto menu

:imagen
echo.
echo Abriendo una imagen de ejemplo... presiona una tecla para cerrarla.
python clasificador_opencv.py --imagen "dataset-resized\dataset-resized\paper\paper1.jpg"
pause
goto menu

:precision
echo.
python probar_modelo.py --limite 100
pause
goto menu
