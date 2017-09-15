@echo off
setlocal enabledelayedexpansion
cd /d %~dp0
find /i "%~nx0" %0 > nul
rem %errorlevel% = 0 if find operation returns true
if %errorlevel% equ 1 (
    echo start to genarate ip-mac mapping
    echo rem "%~nx0" >> %0
    echo. >> %0
    echo rem winxp-sp2 ip-mac >> %0
    for /l %%i in (0,1,19) do (
        set /a mac_end=%%i+10
        set /a ip_end=%%i+10
        echo rem winxp-sp2-%%i 52-54-00-33-a1-!mac_end! 10.14.24.!ip_end! >> %0
    )
    
    echo. >> %0
    echo rem winxp-sp3 ip-mac >> %0
    for /l %%i in (0,1,19) do (
        set /a mac_end=%%i+10
        set /a ip_end=%%i+50
        echo rem winxp-sp3-%%i 52-54-00-33-b1-!mac_end! 10.14.24.!ip_end! >> %0
    )
    
    echo. >> %0
    echo rem win2k3-sp2 ip-mac >> %0
    for /l %%i in (0,1,19) do (
        set /a mac_end=%%i+10
        set /a ip_end=%%i+160
        echo rem win2k3-sp2-%%i 52-54-00-33-c1-!mac_end! 10.14.24.!ip_end! >> %0
    )
    
    echo. >> %0
    echo rem win7-sp1 ip-mac >> %0
    for /l %%i in (0,1,9) do (
        set /a mac_end=%%i+10
        set /a ip_end=%%i+110
        echo rem win7-sp1-%%i 52-54-00-33-d1-!mac_end! 10.14.24.!ip_end! >> %0
    )    
)

for /f "tokens=1 delims= " %%i in ('getmac ^| find /i "52-54-00"') do set mac=%%i
for /f "tokens=2,4 delims= " %%i in ('find /i "%mac%" %0') do set name=%%i & set ip=%%j
echo %mac% !name! !ip!
find /i "%mac%" %0 > nul
if %errorlevel% equ 0 (
    echo start to set hostname and ip address
    reg add "HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\ComputerName\ActiveComputerName" /v ComputerName /t reg_sz /d !name! /f
    reg add "HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Tcpip\Parameters" /v "NV Hostname" /t reg_sz /d !name! /f
    reg add "HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Tcpip\Parameters" /v Hostname /t reg_sz /d !name! /f
    netsh interface ip set address "本地连接" static !ip! 255.255.255.0 10.14.24.1 1
)

del %0

rem winxp-sp2-test 52-54-00-a7-c4-43 10.14.24.250
rem winxp-sp3-test 52-54-00-a3-48-15 10.14.24.251
rem win2k3-sp2-test 52-54-00-cd-5a-e2 10.14.24.252
rem win7-sp1-test 52-54-00-da-23-6e 10.14.24.253

rem "ip_hostname.bat" 
 
rem winxp-sp2 ip-mac 
rem winxp-sp2-0 52-54-00-33-a1-10 10.14.24.10 
rem winxp-sp2-1 52-54-00-33-a1-11 10.14.24.11 
rem winxp-sp2-2 52-54-00-33-a1-12 10.14.24.12 
rem winxp-sp2-3 52-54-00-33-a1-13 10.14.24.13 
rem winxp-sp2-4 52-54-00-33-a1-14 10.14.24.14 
rem winxp-sp2-5 52-54-00-33-a1-15 10.14.24.15 
rem winxp-sp2-6 52-54-00-33-a1-16 10.14.24.16 
rem winxp-sp2-7 52-54-00-33-a1-17 10.14.24.17 
rem winxp-sp2-8 52-54-00-33-a1-18 10.14.24.18 
rem winxp-sp2-9 52-54-00-33-a1-19 10.14.24.19 
rem winxp-sp2-10 52-54-00-33-a1-20 10.14.24.20 
rem winxp-sp2-11 52-54-00-33-a1-21 10.14.24.21 
rem winxp-sp2-12 52-54-00-33-a1-22 10.14.24.22 
rem winxp-sp2-13 52-54-00-33-a1-23 10.14.24.23 
rem winxp-sp2-14 52-54-00-33-a1-24 10.14.24.24 
rem winxp-sp2-15 52-54-00-33-a1-25 10.14.24.25 
rem winxp-sp2-16 52-54-00-33-a1-26 10.14.24.26 
rem winxp-sp2-17 52-54-00-33-a1-27 10.14.24.27 
rem winxp-sp2-18 52-54-00-33-a1-28 10.14.24.28 
rem winxp-sp2-19 52-54-00-33-a1-29 10.14.24.29 
 
rem winxp-sp3 ip-mac 
rem winxp-sp3-0 52-54-00-33-b1-10 10.14.24.50 
rem winxp-sp3-1 52-54-00-33-b1-11 10.14.24.51 
rem winxp-sp3-2 52-54-00-33-b1-12 10.14.24.52 
rem winxp-sp3-3 52-54-00-33-b1-13 10.14.24.53 
rem winxp-sp3-4 52-54-00-33-b1-14 10.14.24.54 
rem winxp-sp3-5 52-54-00-33-b1-15 10.14.24.55 
rem winxp-sp3-6 52-54-00-33-b1-16 10.14.24.56 
rem winxp-sp3-7 52-54-00-33-b1-17 10.14.24.57 
rem winxp-sp3-8 52-54-00-33-b1-18 10.14.24.58 
rem winxp-sp3-9 52-54-00-33-b1-19 10.14.24.59 
rem winxp-sp3-10 52-54-00-33-b1-20 10.14.24.60 
rem winxp-sp3-11 52-54-00-33-b1-21 10.14.24.61 
rem winxp-sp3-12 52-54-00-33-b1-22 10.14.24.62 
rem winxp-sp3-13 52-54-00-33-b1-23 10.14.24.63 
rem winxp-sp3-14 52-54-00-33-b1-24 10.14.24.64 
rem winxp-sp3-15 52-54-00-33-b1-25 10.14.24.65 
rem winxp-sp3-16 52-54-00-33-b1-26 10.14.24.66 
rem winxp-sp3-17 52-54-00-33-b1-27 10.14.24.67 
rem winxp-sp3-18 52-54-00-33-b1-28 10.14.24.68 
rem winxp-sp3-19 52-54-00-33-b1-29 10.14.24.69 
 
rem win2k3-sp2 ip-mac 
rem win2k3-sp2-0 52-54-00-33-c1-10 10.14.24.160 
rem win2k3-sp2-1 52-54-00-33-c1-11 10.14.24.161 
rem win2k3-sp2-2 52-54-00-33-c1-12 10.14.24.162 
rem win2k3-sp2-3 52-54-00-33-c1-13 10.14.24.163 
rem win2k3-sp2-4 52-54-00-33-c1-14 10.14.24.164 
rem win2k3-sp2-5 52-54-00-33-c1-15 10.14.24.165 
rem win2k3-sp2-6 52-54-00-33-c1-16 10.14.24.166 
rem win2k3-sp2-7 52-54-00-33-c1-17 10.14.24.167 
rem win2k3-sp2-8 52-54-00-33-c1-18 10.14.24.168 
rem win2k3-sp2-9 52-54-00-33-c1-19 10.14.24.169 
rem win2k3-sp2-10 52-54-00-33-c1-20 10.14.24.170 
rem win2k3-sp2-11 52-54-00-33-c1-21 10.14.24.171 
rem win2k3-sp2-12 52-54-00-33-c1-22 10.14.24.172 
rem win2k3-sp2-13 52-54-00-33-c1-23 10.14.24.173 
rem win2k3-sp2-14 52-54-00-33-c1-24 10.14.24.174 
rem win2k3-sp2-15 52-54-00-33-c1-25 10.14.24.175 
rem win2k3-sp2-16 52-54-00-33-c1-26 10.14.24.176 
rem win2k3-sp2-17 52-54-00-33-c1-27 10.14.24.177 
rem win2k3-sp2-18 52-54-00-33-c1-28 10.14.24.178 
rem win2k3-sp2-19 52-54-00-33-c1-29 10.14.24.179 
 
rem win7-sp1 ip-mac 
rem win7-sp1-0 52-54-00-33-d1-10 10.14.24.110 
rem win7-sp1-1 52-54-00-33-d1-11 10.14.24.111 
rem win7-sp1-2 52-54-00-33-d1-12 10.14.24.112 
rem win7-sp1-3 52-54-00-33-d1-13 10.14.24.113 
rem win7-sp1-4 52-54-00-33-d1-14 10.14.24.114 
rem win7-sp1-5 52-54-00-33-d1-15 10.14.24.115 
rem win7-sp1-6 52-54-00-33-d1-16 10.14.24.116 
rem win7-sp1-7 52-54-00-33-d1-17 10.14.24.117 
rem win7-sp1-8 52-54-00-33-d1-18 10.14.24.118 
rem win7-sp1-9 52-54-00-33-d1-19 10.14.24.119 
