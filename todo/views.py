import datetime
from io import BytesIO
import json
from django.http import JsonResponse
import pronotepy
from .models import *
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
#importer le login de django
from django.contrib.auth import authenticate,login as django_login
from django.contrib.auth.decorators import login_required
import uuid
from django.views.decorators.csrf import csrf_exempt
from pyzbar.pyzbar import decode
from PIL import Image
import icalendar
import requests

def importer_edt(client):
    url_ical = client.export_ical()
    response = requests.get(url_ical)
    cal = icalendar.Calendar.from_ical(response.content)

    for component in cal.walk():
        if component.name == "VEVENT":
            start = component.get('DTSTART').dt
            end = component.get('DTEND').dt
            summary = str(component.get('SUMMARY'))
            location = str(component.get('LOCATION') or "")
            description = str(component.get('DESCRIPTION') or "")

            # Facultatif : déduire semaine A ou B selon la date
            semaine = 'A' if (start.isocalendar().week % 2 == 0) else 'B'

            # Enregistre dans la BDD Django
            EmploiDuTemps.objects.create(
                date=start.date(),
                start=start,
                end=end,
                matiere=summary,
                salle=location,
                description=description,
                semaine_type=semaine
            )

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        mon_uuid = str(uuid.uuid4())
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(username=username, email=email, password=password)
            CustomUser.objects.create(user=user, uuid=mon_uuid)
            return render(request, 'index.html', {"message": "oui"})
        else : 
            return render(request, 'index.html', {"message": "non"})

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'index.html', {"caca": "caca"})

@csrf_exempt
@login_required
def dashboard(request):
    user = request.user
    custom_user = CustomUser.objects.get(user=request.user)
    
    try:
        connection = user.connexionpronote
        mon_uuid = custom_user.uuid
        
        now = timezone.now()  # datetime aware
        limite = now - datetime.timedelta(minutes=10)

        if connection.date_connexion < limite:
            return render(request, 'dashboard.html', {"message": "non"})

        client = pronotepy.Client.qrcode_login(
            qr_code={
                "login": connection.login,
                "jeton": connection.jeton,
                "url": connection.url,
                "uuid": mon_uuid,
                "pin": connection.pin,
            },
            pin=connection.pin,
            uuid=connection.uuid
        )

        devoirs = client.homework(datetime.date.today(), datetime.date.today() + datetime.timedelta(days=21))
        print(f"{len(devoirs)} devoirs récupérés depuis Pronote")
        for dev in devoirs:
            #si dev.description n'existe pas dans la db
            if not Devoir.objects.filter(utilisateur=user, consigne=dev.description).exists():
                Devoir.objects.create(
                    utilisateur=user,
                    titre=dev.subject.name, 
                    consigne=dev.description,
                    date_limite=dev.date,
                    est_termine=False
                )
            elif Devoir.objects.filter(utilisateur=user, consigne=dev.description).exists():
                Devoir.objects.filter(utilisateur=user, consigne=dev.description).update(
                    utilisateur=user,
                    titre=dev.subject.name,
                    date_limite=dev.date,
                    est_termine=False
                )
                
        return render(request, 'dashboard.html')

    except ConnexionPronote.DoesNotExist:
        return render(request, 'dashboard.html')


@login_required
def check_pronote_lie(request):
    user = request.user
    try:
        # Vérifie si la connexion Pronote existe et est encore fraîche
        connection = user.connexionpronote
        now = timezone.now()
        is_valid = connection.date_connexion > now - datetime.timedelta(minutes=10)
        return JsonResponse({"message": "oui" if is_valid else "non"})

    except ConnexionPronote.DoesNotExist:
        return JsonResponse({"message": "non"})

@login_required
@csrf_exempt
def url_liee_pronote(request):
    if request.method == "POST":
        qrcode_file = request.FILES.get('qrcode')
        code_pin = request.POST.get('code_pin')

        if not qrcode_file or not code_pin:
            return JsonResponse({"message": "error", "detail": "QR code ou code PIN manquant"}, status=400)

        try:
            image = Image.open(qrcode_file)
            decoded_objects = decode(image)

            if not decoded_objects:
                return JsonResponse({"message": "error", "detail": "Aucun QR code détecté"}, status=400)

            qr_code_data_str = decoded_objects[0].data.decode('utf-8')
            qr_code_dict = json.loads(qr_code_data_str)

            if not all(k in qr_code_dict for k in ("jeton", "login", "url")):
                return JsonResponse({"message": "error", "detail": "QR code incomplet"}, status=400)

        except Exception as e:
            return JsonResponse({"message": "error", "detail": f"Erreur décodage QR code : {str(e)}"}, status=400)

        try:
            try:
                custom_user = CustomUser.objects.get(user=request.user)
                mon_uuid = custom_user.uuid
            except CustomUser.DoesNotExist:
                mon_uuid = str(uuid.uuid4())

            client = pronotepy.Client.qrcode_login(qr_code=qr_code_dict, pin=code_pin, uuid=mon_uuid)
            
            
            ConnexionPronote.objects.update_or_create(
                utilisateur=request.user,
                defaults={
                    "jeton": qr_code_dict.get("jeton"),
                    "login": qr_code_dict.get("login"),
                    "url": qr_code_dict.get("url"),
                    "uuid": mon_uuid,
                    "pin": code_pin,
                }
            )
            
            devoirs = client.homework(datetime.date.today(), datetime.date.today() + datetime.timedelta(days=365))
            for devoir in devoirs:
                if not Devoir.objects.filter(utilisateur=request.user, consigne=devoir.description).exists():
                    Devoir.objects.create(
                        utilisateur=request.user,
                        titre=devoir.subject.name,
                        consigne=devoir.description,
                        date_limite=devoir.date,
                        est_termine=False
                    )
                elif Devoir.objects.filter(utilisateur=request.user, consigne=devoir.description).exists():
                    Devoir.objects.filter(utilisateur=request.user, consigne=devoir.description).update(
                        utilisateur=request.user,
                        titre=devoir.subject.name,
                        date_limite=devoir.date,
                        est_termine=False
                    )
            
            
            

            return JsonResponse({"message": "ok", "detail": "Connexion Pronote liée"})

        except Exception as e:
            return JsonResponse({"message": "error", "detail": f"Erreur connexion Pronote : {str(e)}"}, status=400)

    # <-- Ce code ne sera exécuté que si ce n'était PAS un POST
    return JsonResponse({"message": "method_not_allowed"}, status=405)


@login_required
def get_devoirs_database(request):
    devoirs = Devoir.objects.filter(utilisateur=request.user)
    return JsonResponse({"status": "succes", "devoirs": list(devoirs.values())})

@login_required
def get_emploit_du_temps(request):
    pass