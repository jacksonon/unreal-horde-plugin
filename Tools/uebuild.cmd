@echo off
setlocal

set SCRIPT_DIR=%~dp0
set PYTHON=python

%PYTHON% "%SCRIPT_DIR%uebuild.py" %*
exit /b %ERRORLEVEL%

