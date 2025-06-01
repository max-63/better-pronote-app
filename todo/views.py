import datetime
from io import BytesIO
import json
from zoneinfo import ZoneInfo
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
from django.utils import timezone



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
    connexion = ConnexionPronote.objects.get(utilisateur=user)
    now = timezone.now()
    print(connexion.date_connexion , now)
    temps_ecoule = now - connexion.date_connexion
    # Si le temps écoulé est strictement entre 5 et 10 minutes
    if temps_ecoule < timedelta(minutes=10):
        print('cool')
        client = pronotepy.Client.qrcode_login(
            qr_code={
                "login": connexion.login,
                "jeton": connexion.jeton,
                "url": connexion.url,
                "uuid": custom_user.uuid,
                "pin": connexion.pin,
            },
            pin=connexion.pin,
            uuid=connexion.uuid
        )
        
        new_qr = client.request_qr_code_data(pin=str(connexion.pin))
        print("new_qr =", new_qr)

        # enregistrer les nouveaux truc dans la db        
        # connexion.login = new_qr["login"]
        # connexion.jeton = new_qr["jeton"]
        connexion.url = new_qr["url"]
        # connexion.date_connexion = timezone.now()
        connexion.save()
        
        client = pronotepy.Client.qrcode_login(
            qr_code={
                "login": connexion.login,
                "jeton": connexion.jeton,
                "url": connexion.url,
                "uuid": custom_user.uuid,
                "pin": connexion.pin,
            },
            pin=connexion.pin,
            uuid=connexion.uuid
        )
        
        devoirs = client.homework(datetime.date.today(), datetime.date.today() + timedelta(days=21))
        print(f"{len(devoirs)} devoirs récupérés depuis Pronote")
        for dev in devoirs:
            #si dev.description n'existe pas dans la db + dev.date n'existe pas dans la db
            if not Devoir.objects.filter(utilisateur=user, consigne=dev.description, date_limite=dev.date).exists():

                Devoir.objects.create(
                    utilisateur=user,
                    titre=dev.subject.name, 
                    consigne=dev.description,
                    date_limite=dev.date,
                    est_termine=False
                )

        notes = client.current_period.grades
        for grade in notes:
            print(f"Matière : {grade.subject.name}")
            print(f"Note     : {grade.grade}")
            print(f"Sur      : {grade.out_of}")
            print(f"Coef     : {grade.coefficient}")
            print(f"Date     : {grade.date}")
            print(f"Prof     : {grade}")
            print("-" * 30)        
    
        return render(request, 'dashboard.html')
    
    return render(request, 'dashboard.html')    



@login_required
def check_pronote_lie(request):
    user = request.user
    try:
        connexion = ConnexionPronote.objects.get(utilisateur=user)
    except ConnexionPronote.DoesNotExist:
        return JsonResponse({"message": "non lie"})

    now = timezone.now()
    temps_ecoule = now - connexion.date_connexion

    # Si la connexion date de moins de 10 minutes
    if temps_ecoule < timedelta(minutes=10):
        return JsonResponse({"message": "lie"})
    else:
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
            
            if not ConnexionPronote.objects.filter(utilisateur=request.user).exists():
                ConnexionPronote.objects.create(
                    utilisateur=request.user,
                    jeton=qr_code_dict.get("jeton"),
                    login=qr_code_dict.get("login"),
                    url=qr_code_dict.get("url"),
                    uuid=mon_uuid,
                    pin=code_pin,
                    date_connexion=timezone.now()
                )
            else:
                connexion = ConnexionPronote.objects.get(utilisateur=request.user)
                connexion.jeton = qr_code_dict.get("jeton")
                connexion.login = qr_code_dict.get("login")
                connexion.url = qr_code_dict.get("url")
                connexion.uuid = mon_uuid
                connexion.pin = code_pin
                connexion.date_connexion = timezone.now()
                connexion.save()
            
            
            devoirs = client.homework(datetime.date.today(), datetime.date.today() + timedelta(days=365))
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