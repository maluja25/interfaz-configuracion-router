@echo off
echo Activando entorno virtual para Router Manager...
call venv\Scripts\activate.bat
echo.
echo ✅ Entorno virtual activado!
echo.
echo Para ejecutar la aplicación, use:
echo   python main.py
echo.
echo Para desactivar el entorno virtual, use:
echo   deactivate
echo.
cmd /k
