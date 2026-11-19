@echo off
chcp 65001 > nul
title WebOrder Telegram Bot
echo =======================================================
echo   Запуск WebOrder Telegram Bot (Windows)
echo =======================================================
echo.
cd /d "%~dp0"

if not exist .env (
    echo [ВНИМАНИЕ] Файл .env не найден! Скопируйте .env.example в .env
    pause
    exit /b 1
)

if exist venv\Scripts\python.exe (
    echo [INFO] Запуск через виртуальное окружение venv...
    venv\Scripts\python.exe main.py
) else (
    echo [INFO] Запуск через системный python...
    python main.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ОШИБКА] Бот завершил работу с ошибкой.
    pause
)
