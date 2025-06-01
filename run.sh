#!/bin/bash

# Lancer le worker Django en arrière-plan
echo "🚀 Lancement du worker django-background-tasks..."
python manage.py process_tasks &

# Lancer le serveur de développement
echo "🌍 Lancement du serveur Django en développement..."
python manage.py runserver
