pip install pymongo
pip install websockets
cls

@echo off

echo Initiating database
python adddb.py
echo Done

echo Starting in 3 seconds
timeout /t 3 /nobreak >nul
cls

echo Starting the server
python server.py
pause