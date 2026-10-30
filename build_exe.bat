@echo off
title Sarki Sozu Senkronlayici - EXE Builder
echo ========================================================
echo   Sarki Sozu Senkronlayici / Lyrics Synchronizer
echo   EXE Derleme Sihirbazi / Build Executable
echo ========================================================
echo.
echo [1/2] Gerekli paketler kontrol ediliyor...
python -m pip install -r requirements.txt pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] Paketler yuklenirken bir sorun olustu!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] PyInstaller ile EXE olusturuluyor...
python -m PyInstaller --noconfirm --onedir --windowed --name "SarkiSozuSenkron" --collect-all customtkinter sarki_sozu_senkron.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] EXE olusturma sirasinda bir hata olustu!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo   Derleme Basariyla Tamamlandi!
echo   EXE Dosyasi: dist\SarkiSozuSenkron\SarkiSozuSenkron.exe
echo ========================================================
echo.
pause
