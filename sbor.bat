@echo off
setlocal enabledelayedexpansion

::: Настройки :::
set "logpath=\\OITS02\11\%computername%.txt"
set "tempfile=%temp%\pc_info.tmp"

::: Проверка доступности сетевого ресурса :::
if not exist "\\OITS02\11\" (
    echo Ошибка: Сетевой ресурс \\OITS02\11 недоступен!
    pause
    exit /b 1
)

::: Очистка старого файла ::-
if exist "%logpath%" del "%logpath%"

::: Сбор информации ::-
(
    echo ===== Системная информация =====
    echo [Имя ПК]: %computername%
    
    ::: IP-адрес :::
    for /f "tokens=2 delims=[]" %%i in ('ping -n 1 -4 %computername% ^| findstr "["') do set "ip=%%i"
    echo [IP-адрес]: !ip!
    
    echo [Пользователь]: %username%
    
    ::: Модель ноутбука :::
    for /f "skip=1 delims=" %%Z in ('wmic computersystem get model ^| findstr /v "^$"') do (
        echo [Модель]: %%Z
        goto :break_model
    )
    :break_model
    
    ::: Процессор :::
    echo [Процессор]:
    set "count=0"
    for /f "skip=1 delims=" %%i in ('wmic cpu get name ^| findstr /v "^$"') do (
        set /a "count+=1"
        echo   Ядро !count!: %%i
    )
    
    ::: Материнская плата :::
    for /f "skip=1 delims=" %%Z in ('wmic baseboard get product ^| findstr /v "^$"') do (
        echo [Материнская плата]: %%Z
        goto :break_mb
    )
    :break_mb
    
    ::: Оперативная память :::
    echo [Оперативная память]:
    set "count=0"
    for /f "skip=1 tokens=1-5 delims= " %%A in ('wmic memorychip get partnumber^, capacity^, speed^, manufacturer /format:list ^| findstr "="') do (
        set /a "count+=1"
        echo   Планка !count!:
        echo     Производитель: %%A
        echo     Модель: %%B
        echo     Объем: %%(%%C /1073741824) ГБ
        echo     Частота: %%D МГц
    )
    
    ::: Диски :::
    echo [Накопители]:
    set "count=0"
    for /f "skip=1 tokens=1-2 delims= " %%A in ('wmic diskdrive get model^, size ^| findstr /v "^$"') do (
        set /a "count+=1"
        set "size=%%B"
        set "size=!size:~0,-3!"
        echo   Диск !count!: %%A [!size! ГБ]
    )
    
    echo ===== Конец отчета =====
) > "%tempfile%"

::: Проверка и запись :::
if exist "%tempfile%" (
    type "%tempfile%" >> "%logpath%"
    del "%tempfile%"
    echo Информация сохранена: %logpath%
) else (
    echo Ошибка создания файла!
)

pause
