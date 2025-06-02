from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=36, unique=True)

class Notes(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    matiere  = models.TextField()
    note = models.TextField()
    sur = models.TextField()
    coef = models.CharField(max_length=10)
    date = models.DateField()

    
    
class EmploiDuTemps(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    matiere = models.CharField(max_length=100)
    salle = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.matiere} - {self.utilisateur.username}"

class Devoir(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    consigne = models.TextField()
    date_limite = models.DateField()
    est_termine = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.titre} - {self.utilisateur.username}"

class SousTache(models.Model):
    devoir = models.OneToOneField(Devoir, on_delete=models.CASCADE, related_name="sous_taches")
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duree_minutes = models.IntegerField(default=30)
    est_terminee = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.titre} ({self.devoir.titre})"

class Indisponibilite(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    jour = models.CharField(max_length=10)  # ex: 'Lundi' ou 'Temporaire'
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    description = models.CharField(max_length=255, blank=True)
    temporaire = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def est_expiree(self):
        if self.temporaire:
            return timezone.now() > self.date_creation + timedelta(days=7)
        return False

    def __str__(self):
        return f"Indispo {self.jour} {self.heure_debut}-{self.heure_fin} ({self.utilisateur.username})"

class TachePlanifiee(models.Model):
    sous_tache = models.ForeignKey(SousTache, on_delete=models.CASCADE)
    date = models.DateField()
    heure_debut = models.TimeField()
    duree_minutes = models.IntegerField()
    est_terminee = models.BooleanField(default=False)

    def __str__(self):
        return f"Tâche planifiée: {self.sous_tache.titre} le {self.date} à {self.heure_debut}"

class ConnexionPronote(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    jeton = models.TextField()
    login = models.TextField()
    url = models.TextField()
    date_connexion = models.DateTimeField(auto_now_add=True)
    uuid = models.CharField(max_length=36) 
    pin = models.CharField(max_length=4)
    username = models.TextField()
    password = models.TextField()

