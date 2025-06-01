# 📋 Cahier des Charges - Application Planificateur Intelligent de Devoirs 🧠🗓️

---

## 1. Contexte et Objectifs 🎯

Cette application est conçue pour les collégiens et lycéens (12-18 ans) qui veulent gérer leurs devoirs facilement et prendre de l’avance sans stress.

**Objectifs principaux :**

- 📥 Saisir les devoirs.
- 🤖 Utiliser une IA gratuite pour analyser et découper les devoirs en étapes (introduction, rédaction, conclusion, recherche…).
- 📅 Planifier automatiquement ces étapes dans un calendrier adapté à ton emploi du temps, tes indisponibilités et préférences.
- 📊 Suivre ta progression avec une barre d’avancement et un système de sous-tâches.
- ⏲️ Intégrer un timer pour gérer ton temps de travail et booster ta concentration.
- 🔄 Ajuster automatiquement le planning en fonction de tes disponibilités ou indisponibilités.

---

## 2. Public Cible 👨‍🎓👩‍🎓

- **Collégiens** (12-15 ans) : Interface simple, découpage automatique des devoirs longs, gestion facile.
- **Lycéens** (15-18 ans) : Gestion plus fine avec sous-tâches détaillées, priorités, notifications et suivi avancé.

---

## 3. Fonctionnalités Principales ⚙️

### 3.1 Gestion des devoirs 📚

- ✍️ Saisie manuelle.
- 🧠 IA pour découpage automatique des devoirs en sous-tâches.
- 🛠️ Modification manuelle des étapes générées.

### 3.2 Planification intelligente 🤖📅

- 📆 Calendrier personnel intégrant cours, activités et indisponibilités.
- 🚫 Gestion des créneaux d’indisponibilité permanents ou temporaires (avec suppression automatique au bout d’une semaine).
- 🤓 Algorithme qui répartit les sous-tâches sur les créneaux libres.
- ⏳ Respect strict des dates limites.
- 👁️ Interface interactive avec possibilité d’ajustements manuels.

### 3.3 Suivi et gestion du temps ⏰

- ✅ Suivi de l’avancement des sous-tâches.
- 📈 Barre de progression visible sur chaque devoir et globalement.
- 🍅 Timer Pomodoro pour favoriser la concentration (ex : 25 min travail / 5 min pause).
- 🔔 Notifications et rappels non intrusifs.

### 3.4 Gestion des utilisateurs 👤

- 🔐 Inscription et authentification sécurisée.
- ⚙️ Gestion du profil et préférences.
- ☁️ Sauvegarde des données dans le cloud.

---

## 4. Architecture Technique 🛠️

- Backend : Django REST Framework pour API et gestion des données.
- Frontend : Angular pour une interface réactive et mobile-friendly.
- Base de données : PostgreSQL.
- IA hébergée sur un cloud gratuit type GrocCloud.

---

## 5. Modèles de données (Django) 🗃️

### Devoirs 📋
Titre, consignes, date limite, état (terminé ou non).

### Sous-tâches 🔨
Étapes du devoir (introduction, rédaction…), durée estimée, statut.

### Indisponibilités 🚫
Plages horaires où tu ne peux pas travailler.  
**Peuvent être permanentes (ex : sport hebdo) ou temporaires (ex : vacances) avec suppression auto après 7 jours.**

### Tâches planifiées 🕒
Organisation des sous-tâches dans le calendrier (date, heure, durée).

---

## 6. Flux Utilisateur 🚦

1. Saisie ou import d’un devoir.
2. IA analyse et découpe en sous-tâches.
3. Validation ou modification des sous-tâches.
4. Définition de la date limite.
5. Génération automatique du planning selon tes disponibilités.
6. Suivi via calendrier et barre de progression.
7. Timer pour t’aider à rester focus.
8. Mise à jour automatique du planning si tu changes tes disponibilités.

---

## 7. Contraintes ⚠️

- IA gratuite et stable.
- Sécurité des données et authentification.
- Responsive design (mobile/tablette/PC).
- Simple et accessible pour les 12-18 ans.
- Notifications efficaces mais pas gênantes.

---

## 8. Évolutions futures 🚀

- Synchronisation Google Calendar.
- Notifications push.
- Statistiques d’efficacité et temps passé.
- Conseils personnalisés pour pauses et révisions.

---

## 9. Structure Django : `models.py` 🐍

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Devoir(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    consigne = models.TextField()
    date_limite = models.DateField()
    est_termine = models.BooleanField(default=False)

class SousTache(models.Model):
    devoir = models.ForeignKey(Devoir, on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duree_minutes = models.IntegerField(default=30)
    est_terminee = models.BooleanField(default=False)

class Indisponibilite(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    jour = models.CharField(max_length=10)  # Exemple : 'Lundi' ou 'Temporaire'
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    description = models.CharField(max_length=255, blank=True)
    temporaire = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def est_expiree(self):
        if self.temporaire:
            return timezone.now() > self.date_creation + timedelta(days=7)
        return False

class TachePlanifiee(models.Model):
    sous_tache = models.ForeignKey(SousTache, on_delete=models.CASCADE)
    date = models.DateField()
    heure_debut = models.TimeField()
    duree_minutes = models.IntegerField()
    est_terminee = models.BooleanField(default=False)
