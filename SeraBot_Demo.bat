@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"

rem Each foreground WSL command has its own terminal and lifetime.
where wsl.exe >nul 2>nul
if errorlevel 1 goto no_wsl
if not exist "scripts\demo\serabot_demo.sh" goto missing_helper
if /I "%~1"=="--dry-run" goto dry_run
if /I "%~1"=="--check" goto check_only
if not "%~1"=="" goto usage

echo Checking Ubuntu-26.04 and the built ROS workspace...
wsl.exe -d Ubuntu-26.04 --cd "%CD%" -e bash scripts/demo/serabot_demo.sh check
if errorlevel 1 goto check_failed

start "SeraBot - Robot and RViz" cmd.exe /k wsl.exe -d Ubuntu-26.04 --cd "%CD%" -e bash scripts/demo/serabot_demo.sh robot
start "SeraBot - IMU plot" cmd.exe /k wsl.exe -d Ubuntu-26.04 --cd "%CD%" -e bash scripts/demo/serabot_demo.sh imu
start "SeraBot - Behavior states" cmd.exe /k wsl.exe -d Ubuntu-26.04 --cd "%CD%" -e bash scripts/demo/serabot_demo.sh states
echo Started three terminals. Gazebo and RViz may take 10-20 seconds to appear.
echo To stop the robot, press Ctrl+C in the Robot and RViz terminal.
exit /b 0

:check_only
wsl.exe -d Ubuntu-26.04 --cd "%CD%" -e bash scripts/demo/serabot_demo.sh check
exit /b %errorlevel%

:dry_run
echo DRY RUN: no WSL distribution, simulation or GUI will be started.
echo [CHECK] wsl.exe -d Ubuntu-26.04 --cd "%CD%" -e bash scripts/demo/serabot_demo.sh check
echo [ROBOT] wsl.exe -d Ubuntu-26.04 --cd "%CD%" -e bash scripts/demo/serabot_demo.sh robot
echo [IMU] wsl.exe -d Ubuntu-26.04 --cd "%CD%" -e bash scripts/demo/serabot_demo.sh imu
echo [STATES] wsl.exe -d Ubuntu-26.04 --cd "%CD%" -e bash scripts/demo/serabot_demo.sh states
exit /b 0

:no_wsl
echo ERROR: wsl.exe was not found. This launcher requires Windows with WSL2.
goto failed
:missing_helper
echo ERROR: scripts\demo\serabot_demo.sh was not found.
echo Keep this BAT file in the root of the SeraBot repository.
goto failed
:check_failed
echo ERROR: the preflight check failed. Read the message above.
goto failed
:usage
echo Usage: SeraBot_Demo.bat [--check or --dry-run]
exit /b 2
:failed
pause
exit /b 1
