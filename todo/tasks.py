from background_task import background
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+
from .models import ConnexionPronote, CustomUser
import pronotepy
from django.utils import timezone

@background(schedule=60)  # exécute la tâche 60 secondes après l'appel
def refresh_all_qrcodes():
    # On prend l'heure Europe/Paris courante avec timezone info
    now = timezone.now(ZoneInfo("Europe/Paris"))
    
    connexions = ConnexionPronote.objects.all()
    for connexion in connexions:
        
        connexion_date = connexion.date_connexion
        
        temps_ecoule = now - connexion_date
        print(connexion.login)
        
        if temps_ecoule < timedelta(minutes=10):
            try:
                custom_user = CustomUser.objects.get(user=connexion.utilisateur)
                client = pronotepy.Client.qrcode_login(
                    qr_code={
                        "login": connexion.login,
                        "jeton": connexion.jeton,
                        "url": connexion.url,
                        "uuid": custom_user.uuid,
                        "pin": connexion.pin,
                    },
                    pin=connexion.pin,
                    uuid=custom_user.uuid,
                )
                new_qr = client.request_qr_code_data(pin=str(connexion.pin))
                connexion.login = new_qr["login"]
                connexion.jeton = new_qr["jeton"]
                connexion.url = new_qr["url"]
                connexion.date_connexion = timezone.now()
                print('chngé', connexion.login)
                connexion.save()
                print(f"QR code rafraîchi pour {connexion.utilisateur}")
            except Exception as e:
                print(f"Erreur pour {connexion.utilisateur}: {e}")
                
                
# from todo.tasks import refresh_all_qrcodes
# refresh_all_qrcodes(repeat=60)