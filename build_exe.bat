@echo off
chcp 65001 >nul
echo ========================================================
echo   Şarkı Sözü Senkronlayıcı / Lyrics Synchronizer
echo   EXE Derleme Sihirbazı / Build Executable
echo ========================================================
echo.
echo [1/2] Gerekli Python paketleri kontrol ediliyor...
pip install -r requirements.txt pyinstaller
echo.
echo [2/2] PyInstaller ile tek dosya EXE olusturuluyor...
pyinstaller --noconfirm --onedir --windowed --name "SarkiSozuSenkron" --collect-all customtkinter sarki_sozu_senkron.py
echo.
echo ========================================================
echo   Tamamlandı! 
echo   EXE Dosyası: dist\SarkiSozuSenkron\SarkiSozuSenkron.exe
echo ========================================================
pause
