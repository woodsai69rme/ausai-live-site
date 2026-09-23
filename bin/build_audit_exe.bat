@echo off
:: bin/build_audit_exe.bat -- build a standalone Windows .exe for bin\run_audit_subprocess.py
::
:: Produces bin\dist\run_audit_subprocess.exe via `python -m PyInstaller --onefile` so
:: the daily WarRoomDailyAuditPreFlight scheduled task can run WITHOUT requiring
:: Python on the box. The .exe is fully self-contained (~6-10 MB); cold-start adds
:: ~0.5-2s (PyInstaller --onefile self-extract to the user's TEMP dir) vs the
:: ~25-30s wrapper measurement per AUDIT_LOG diagnostic footer.
::
:: PATH-portability note (cont.16-fup-6): PyInstaller is invoked via
:: `python -m PyInstaller --onefile` rather than the bare `pyinstaller` command so
:: the bat works on machines where pip-installed scripts aren't on PATH
:: (e.g. user-level Python installs where Python's Scripts dir isn't in PATH).
:: Module-import detection (`python -c "import PyInstaller"`) is the gate.
::
:: Usage (run from a NORMAL cmd.exe on Windows; --rebuild is the install path):
::     bin\build_audit_exe.bat --rebuild         :: remove old + --onefile rebuild -> bin\dist\
::     bin\build_audit_exe.bat --rebuild-onedir  :: remove old + --onedir rebuild -> bin\dist-onedir\
::     bin\build_audit_exe.bat --ab              :: A/B cold-start benchmark of both built artifacts
::     bin\build_audit_exe.bat --status          :: report PyInstaller + both .exe states
::     bin\build_audit_exe.bat --clean           :: remove bin\dist\, bin\dist-onedir\, bin\build\, bin\build-onedir\, .spec(s)
::     bin\build_audit_exe.bat --help            :: this message
::
:: Prerequisite:  PyInstaller installed in the active Python env. Install with:
::                  python -m pip install pyinstaller
::
:: Output is a per-machine release artifact. `bin\dist\`, `bin\build\`, and
:: `bin\*.spec` are .gitignored (Pass-15 of the .gitignore hygiene sweep).
::
:: Cross-references:
::   - bin\install_AUDIT_scheduler_RUNBOOK.md  -- "Distribution" section has operator workflow
::   - bin\run_audit_subprocess.py             -- "Distribution (PyInstaller --onefile)" section
::   - CHANGELOG.md ## 2026-07-10 (cont.16-fup-6) -- migration rationale

setlocal

set "REPO=%~dp0.."
set "SCRIPT=%REPO%\bin\run_audit_subprocess.py"
set "DIST=%REPO%\bin\dist"
set "DIST_ONEDIR=%REPO%\bin\dist-onedir"
set "BUILD=%REPO%\bin\build"
set "BUILD_ONEDIR=%REPO%\bin\build-onedir"
set "SPECPATH=%REPO%\bin"
set "EXE=%DIST%\run_audit_subprocess.exe"
set "EXE_ONEDIR=%DIST_ONEDIR%\run_audit_subprocess.exe"

:: --- Flag dispatcher (no ( ... ) blocks per v26 lesson) ---
if /i "%~1"=="--help"             goto :show_help
if /i "%~1"==""--help"            goto :show_help
if /i "%~1"=="--status"           goto :do_status
if /i "%~1"=="--rebuild"          goto :do_rebuild
if /i "%~1"=="--rebuild-onedir"   goto :do_rebuild_onedir
if /i "%~1"=="--ab"               goto :do_ab_benchmark
if /i "%~1"=="--clean"            goto :do_clean
goto :show_help

:do_rebuild
python -c "import PyInstaller" >nul 2>&1
if not "%errorlevel%"=="0" goto :no_pyi

echo.
echo [build_audit_exe] Cleaning previous artifacts...
if exist "%DIST%"   rmdir /S /Q "%DIST%"
if exist "%BUILD%"  rmdir /S /Q "%BUILD%"
if exist "%SPECPATH%\run_audit_subprocess.spec" del "%SPECPATH%\run_audit_subprocess.spec" >nul 2>&1
echo.

echo [build_audit_exe] Running:
echo   python -m PyInstaller --onefile --noconfirm --clean ^|
echo            --name run_audit_subprocess ^|
echo            --distpath "%DIST%" ^|
echo            --workpath "%BUILD%" ^|
echo            --specpath "%SPECPATH%" ^|
echo            "%SCRIPT%"
echo.
python -m PyInstaller --onefile --noconfirm --clean ^
    --name run_audit_subprocess ^
    --distpath "%DIST%" ^
    --workpath "%BUILD%" ^
    --specpath "%SPECPATH%" ^
    "%SCRIPT%"
set "PYI_RC=%errorlevel%"
if not "%PYI_RC%"=="0" goto :pyinstaller_fail

echo.
if not exist "%EXE%" goto :no_exe_after

echo [PASS] built: %EXE%
echo.
echo Next steps:
echo   1. Smoke-test:    "%EXE%" --help
echo   2. Install task:  bin\install_AUDIT_scheduler.bat  ^(elevated cmd.exe^)
echo.
endlocal
exit /b 0

:pyinstaller_fail
echo.
echo [FAIL] python -m PyInstaller returned errorlevel %PYI_RC%.
echo        Hint: inspect the build log above for hidden-import errors.
echo        (Per the cont.16-fup-6 PATH-portability note; the bat invokes
echo        the module via `python -m` so path-resolution isn't the cause.)
endlocal
exit /b 1

:do_rebuild_onedir
python -c "import PyInstaller" >nul 2>&1
if not "%errorlevel%"=="0" goto :no_pyi

echo.
echo [build_audit_exe] Cleaning previous onedir artifacts...
if exist "%DIST_ONEDIR%"   rmdir /S /Q "%DIST_ONEDIR%"
if exist "%BUILD_ONEDIR%"  rmdir /S /Q "%BUILD_ONEDIR%"
if exist "%SPECPATH%\run_audit_subprocess_onedir.spec" del "%SPECPATH%\run_audit_subprocess_onedir.spec" >nul 2>&1
echo.

echo [build_audit_exe] Running:
echo   python -m PyInstaller --onedir --noconfirm --clean ^
echo            --name run_audit_subprocess ^
echo            --distpath "%DIST_ONEDIR%" ^
echo            --workpath "%BUILD_ONEDIR%" ^
echo            --specpath "%SPECPATH%" ^
echo            "%SCRIPT%"
echo.
python -m PyInstaller --onedir --noconfirm --clean ^
    --name run_audit_subprocess ^
    --distpath "%DIST_ONEDIR%" ^
    --workpath "%BUILD_ONEDIR%" ^
    --specpath "%SPECPATH%" ^
    "%SCRIPT%"
set "PYI_RC=%errorlevel%"
if not "%PYI_RC%"=="0" goto :pyinstaller_fail

echo.
if not exist "%EXE_ONEDIR%" goto :no_onedir_after

echo [PASS] built: %EXE_ONEDIR%
echo.
echo Notes:
echo   --onedir ships as bin\dist-onedir\run_audit_subprocess.exe alongside
echo   runtime DLLs. Cold-start is typically ~0.15s vs ~0.49s for --onefile.
echo   Update bin\install_AUDIT_scheduler_RUNBOOK.md "Distribution" section
echo   to point the scheduled task at the new path if you want to migrate.
echo.
endlocal
exit /b 0

:no_onedir_after
echo [FAIL] python -m PyInstaller rc=0 succeeded but "%EXE_ONEDIR%" was not produced.
echo        Check the build log for hidden warnings or stripped-binary issues.
endlocal
exit /b 1

:do_ab_benchmark
echo.
echo [build_audit_exe] A/B cold-start benchmark (--onefile vs --onedir)
echo.

if not exist "%EXE%"        echo   WARN: --onefile  artifact missing: %EXE%         (run --rebuild first)
if not exist "%EXE_ONEDIR%" echo   WARN: --onedir   artifact missing: %EXE_ONEDIR%  (run --rebuild-onedir first)

if not exist "%EXE%"        goto :ab_skip_onefile
if not exist "%EXE_ONEDIR%" goto :ab_skip_onedir

set "REPORT=%REPO%\bin\dist\ab_coldstart_20260711.json"

echo Running --onefile --help x3...
set "OF1=" & set "OF2=" & set "OF3="
for /f "tokens=2 delims=,:" %%a in ('powershell -NoProfile -Command "$sw=[Diagnostics.Diagnostics.Stopwatch]::StartNew(); & '%EXE%' --help ^| Out-Null; $sw.Stop(); Write-Host ('t=' + $sw.Elapsed.TotalSeconds.ToString('0.000'))"') do set "OF1=%%a"
for /f "tokens=2 delims=,:" %%a in ('powershell -NoProfile -Command "$sw=[Diagnostics.Diagnostics.Stopwatch]::StartNew(); & '%EXE%' --help ^| Out-Null; $sw.Stop(); Write-Host ('t=' + $sw.Elapsed.TotalSeconds.ToString('0.000'))"') do set "OF2=%%a"
for /f "tokens=2 delims=,:" %%a in ('powershell -NoProfile -Command "$sw=[Diagnostics.Diagnostics.Stopwatch]::StartNew(); & '%EXE%' --help ^| Out-Null; $sw.Stop(); Write-Host ('t=' + $sw.Elapsed.TotalSeconds.ToString('0.000'))"') do set "OF3=%%a"

echo Running --onedir --help x3...
set "OD1=" & set "OD2=" & set "OD3="
for /f "tokens=2 delims=,:" %%a in ('powershell -NoProfile -Command "$sw=[Diagnostics.Diagnostics.Stopwatch]::StartNew(); & '%EXE_ONEDIR%' --help ^| Out-Null; $sw.Stop(); Write-Host ('t=' + $sw.Elapsed.TotalSeconds.ToString('0.000'))"') do set "OD1=%%a"
for /f "tokens=2 delims=,:" %%a in ('powershell -NoProfile -Command "$sw=[Diagnostics.Diagnostics.Stopwatch]::StartNew(); & '%EXE_ONEDIR%' --help ^| Out-Null; $sw.Stop(); Write-Host ('t=' + $sw.Elapsed.TotalSeconds.ToString('0.000'))"') do set "OD2=%%a"
for /f "tokens=2 delims=,:" %%a in ('powershell -NoProfile -Command "$sw=[Diagnostics.Diagnostics.Stopwatch]::StartNew(); & '%EXE_ONEDIR%' --help ^| Out-Null; $sw.Stop(); Write-Host ('t=' + $sw.Elapsed.TotalSeconds.ToString('0.000'))"') do set "OD3=%%a"

echo.
echo === A/B COLD-START RESULTS (3 trials each) ===
echo --onefile:  %OF1%s / %OF2%s / %OF3%s
echo --onedir :  %OD1%s / %OD2%s / %OD3%s
python -c "import json,statistics; of=[float('%OF1%'),float('%OF2%'),float('%OF3%')]; od=[float('%OD1%'),float('%OD2%'),float('%OD3%')]; rep={'onefile_trials':of,'onedir_trials':od,'onefile_p50':round(statistics.median(of),3),'onefile_mean':round(statistics.mean(of),3),'onedir_p50':round(statistics.median(od),3),'onedir_mean':round(statistics.mean(od),3),'speedup_factor':round(statistics.median(of)/statistics.median(od),2) if statistics.median(od) else None}; open(r'%REPORT%','w',encoding='utf-8').write(json.dumps(rep,indent=2)); print(f\"onefile p50 = {rep['onefile_p50']}s\"); print(f\"onedir  p50 = {rep['onedir_p50']}s\"); print(f\"speedup      = {rep['speedup_factor']}x\"); print(f\"report -> {r'%REPORT%'}\")"
echo.
endlocal
exit /b 0

:ab_skip_onefile
echo.
echo [SKIP] --onefile artifact not found at %EXE%. Build it with --rebuild first.
echo        Mirrors the SKIP-on-skip-cond UX only when --rebuild was never run.
endlocal
exit /b 2

:ab_skip_onedir
echo.
echo [SKIP] --onedir artifact not found at %EXE_ONEDIR%. Build it with --rebuild-onedir first.
endlocal
exit /b 2

:no_exe_after
echo [FAIL] python -m PyInstaller rc=0 succeeded but "%EXE%" was not produced.
echo        Check the build log for hidden warnings or stripped-binary issues.
endlocal
exit /b 1

:no_pyi
echo [FAIL] PyInstaller is not importable in the active Python env.
echo        Install with: python -m pip install pyinstaller
echo        (This bat uses `python -c "import PyInstaller"` to gate so
echo        pip-installed Scripts not being on PATH doesn't matter.)
endlocal
exit /b 1

:do_clean
echo [build_audit_exe] Cleaning artifacts...
if exist "%DIST%"         rmdir /S /Q "%DIST%"
if exist "%DIST_ONEDIR%"  rmdir /S /Q "%DIST_ONEDIR%"
if exist "%BUILD%"        rmdir /S /Q "%BUILD%"
if exist "%BUILD_ONEDIR%" rmdir /S /Q "%BUILD_ONEDIR%"
if exist "%SPECPATH%\run_audit_subprocess.spec"         del "%SPECPATH%\run_audit_subprocess.spec"         >nul 2>&1
if exist "%SPECPATH%\run_audit_subprocess_onedir.spec"  del "%SPECPATH%\run_audit_subprocess_onedir.spec"  >nul 2>&1
echo [PASS] removed: bin\dist\, bin\dist-onedir\, bin\build\, bin\build-onedir\, .spec(s)
endlocal
exit /b 0

:do_status
echo.
echo [build_audit_exe] STATUS
echo.
echo PyInstaller module:
python -c "import PyInstaller; print('  ' + PyInstaller.__version__)" 2>nul
if not "%errorlevel%"=="0" echo   NOT INSTALLED  ^(. run `python -m pip install pyinstaller` to add^)
echo.
echo source: %SCRIPT%
if exist "%SCRIPT%" (
    echo   EXISTS
) else (
    echo   MISSING
)
echo.
echo --onefile artifact: %EXE%
if exist "%EXE%" (
    echo   EXISTS  ^(.exe present; audit-scheduler XML Command points here^)
) else (
    echo   MISSING  ^(.run `bin\build_audit_exe.bat --rebuild` to build^)
)
echo.
echo --onedir artifact: %EXE_ONEDIR%
if exist "%EXE_ONEDIR%" (
    echo   EXISTS  ^(.exe + sibling DLLs in bin\dist-onedir\^)
) else (
    echo   MISSING  ^(.run `bin\build_audit_exe.bat --rebuild-onedir` to build^)
)
echo.
endlocal
exit /b 0

:show_help
echo.
echo bin\build_audit_exe.bat -- build standalone .exe for bin\run_audit_subprocess.py
echo.
echo Usage:
echo     bin\build_audit_exe.bat --rebuild         :: --onefile variant (single-file .exe; cold-start ~0.49s)
echo     bin\build_audit_exe.bat --rebuild-onedir  :: --onedir variant (dir + .exe; cold-start ~0.15s)
echo     bin\build_audit_exe.bat --ab              :: A/B cold-start benchmark of both built artifacts
echo     bin\build_audit_exe.bat --status          :: report PyInstaller + both .exe states
echo     bin\build_audit_exe.bat --clean           :: remove bin\dist\ + bin\dist-onedir\ + bin\build\ + bin\build-onedir\ + .spec
echo     bin\build_audit_exe.bat --help            :: this message
echo.
echo Prerequisite:      PyInstaller module importable  ^(`python -m pip install pyinstaller`^)
echo Output (onefile):   bin\dist\run_audit_subprocess.exe     ~6-10 MB  cold-start ~0.5-2 s ^(--onefile self-extract to user TEMP^-)
echo Output (onedir):    bin\dist-onedir\run_audit_subprocess.exe + DLLs   cold-start ~0.15 s
echo Wrapper baseline:   ~25-30 s ^(`python bin\run_audit_subprocess.py ...` directly^)
echo.
echo The --ab arm emits a JSON report at bin\dist\ab_coldstart_<DATE>.json with
echo per-trial timings and a speedup factor; mirrors the cont.16-fup-9 cold-start
echo parallelization coercion by making the --onedir trade-off measurable.
echo.
echo See CHANGELOG.md ## 2026-07-10 ^(cont.16-fup-6^) for --onefile migration rationale.
echo See CHANGELOG.md ## 2026-07-11 ^(cont.16-fup-9^) for the --onedir A/B regime.
echo See bin\install_AUDIT_scheduler_RUNBOOK.md "Distribution" section for the
echo operator workflow including scheduling refresh after rebuild.
endlocal
exit /b 0
