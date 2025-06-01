@echo off
echo 🚀 Lancement du worker django-background-tasks...

:: Lance le worker en tâche de fond via PowerShell
powershell -WindowStyle Hidden -Command "Start-Process python -ArgumentList 'manage.py', 'process_tasks' -WindowStyle Hidden"

timeout /t 1 > nul

echo 🌍 Lancement du serveur Django...
python manage.py runserver
