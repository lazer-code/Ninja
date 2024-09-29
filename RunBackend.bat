@echo off

echo Initiating database
python InitiateDatabase.py
echo Done

cd backendserver
echo Starting the server
python server.py
pause