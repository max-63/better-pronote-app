from pronotepy import Client

# Données privées : récupérées après qrcode_login() et stockées en local
pronote_url="https://0630050m.index-education.net/pronote/eleve.html"
username = "acourault"
password = "5B5AB418E359EA32C1B1A1932869797EF1A1351F56D5497005C3152914C16D57F401CFA2B8B7A29581B554A805C6BB6E"
uuid = "1c08770f-1f95-48d7-be0d-6437c7d3cfab"
client_identifier = "0919EF25064A9B703230D1508230DE164A43A5E74752F86861DBBD3B358014AB294C05D17DAACC4EE34C931C760CB42447DA6AB000000000"
device_name = "AdrienPC"

client = Client.token_login(
    pronote_url=pronote_url,
    username=username,
    password=password,
    uuid=uuid,
    client_identifier=client_identifier,
    device_name=device_name
)

if client.logged_in:
    print("✅ Connexion réussie avec token !")
else:
    print("❌ Échec de la connexion.")
