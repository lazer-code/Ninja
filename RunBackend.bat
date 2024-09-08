cd backendserver
@echo off

echo Initiating database
python InitiateDatabase.py
echo Done
echo Starting the server
python server.py
pause