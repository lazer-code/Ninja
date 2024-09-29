@echo off

python InitiateDatabase.py

cd backendserver
python server.py
pause