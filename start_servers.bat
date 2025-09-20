@echo off
echo Starting OSINT Framework Portal...
echo.

echo Starting Flask Backend on port 5000...
start "Flask Backend" cmd /k "cd /d c:\Users\venki\OneDrive\Desktop\final && python app.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting Frontend Server on port 8000...
start "Frontend Server" cmd /k "cd /d c:\Users\venki\OneDrive\Desktop\final && python -m http.server 8000"

echo.
echo ======================================
echo  OSINT Framework Portal Started!
echo ======================================
echo  Backend:  http://localhost:5000
echo  Frontend: http://localhost:8000
echo  Search:   http://localhost:8000/search.html
echo ======================================
echo.
echo Press any key to open the search page...
pause > nul

start http://localhost:8000/search.html

echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
pause