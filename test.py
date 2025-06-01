import pronotepy
import json
import datetime
import time

#JSON
qrcode_data = '{"avecPageConnexion":false,"jeton":"46EE5C74E6947E4606594B9294EA915038FA21878E59F6FDCDDEAD36A62DFB37FF8AAC1E9F6B06BD78471E07507236598CA380D15F71D5FB052689E848E51BE966B247BB6785F2489240F48031269A812BD09F99D6FB8844D7595735D09B191C36935C81BC2D1C8392DF397D1050B827","login":"AF1D0DCAB1FC0316F202C0F4DAD15AF4","url":"https://0630050m.index-education.net/pronote/mobile.eleve.html"}'

# JSON string -> dict Python
qr_code_dict = json.loads(qrcode_data)


import uuid
mon_uuid = str(uuid.uuid4())

# Connexion avec pronotepy
client = pronotepy.Client.qrcode_login(qr_code=qr_code_dict, pin="6080", uuid=mon_uuid)

# Récupérer tous les devoirs disponibles (tous les jours)
# Ici on récupère les devoirs entre aujourd'hui et dans 7 jours
date_debut = datetime.date.today()
date_fin = date_debut + datetime.timedelta(days=7)

while True:
    client = pronotepy.Client.qrcode_login(qr_code=qr_code_dict, pin="6080", uuid=mon_uuid)
    
    print("📅 Devoirs de la semaine :")

    for devoir in client.homework(date_debut, date_fin):
        print(f"📝 Matière : {devoir.subject.name}")
        print(f"📖 Description : {devoir.description}")
        print(f"🗓️ Sujet : {devoir.date}")
        print("-" * 30)
    # attndre 8min
    time.sleep(480)
