@echo off
title Llankay - Iniciador del Proyecto
echo ========================================================
echo               INICIANDO PLATAFORMA LLANKAY
echo ========================================================
echo.

echo [1/3] Iniciando Backend Django en http://127.0.0.1:8000 ...
start "Llankay - Backend Django" cmd /k "cd /d %~dp0backend && .\venv\Scripts\activate && python manage.py runserver"

echo [2/3] Iniciando Frontend Vue 3 en http://localhost:5173 ...
start "Llankay - Frontend Vue" cmd /k "cd /d %~dp0frontend && npm run dev"

echo [3/3] Esperando 3 segundos para abrir navegador...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ========================================================
echo  Todo listo! Backend y Frontend estan corriendo.
echo  Puedes cerrar esta ventana cuando desees.
echo ========================================================
pause
