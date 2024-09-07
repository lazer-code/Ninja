pip install pymongo
pip install websockets
cls

@echo off

echo Initiating database
python InitiateDatabase.py
echo Done

pause
cls

echo Starting the server
python server.py
pause