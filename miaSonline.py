import requests
from datetime import datetime, timedelta

# URL dei due file
url_events = "https://sportsonline.ci/prog.txt"
url_channels = "https://sportzonline.site/247.txt"

# Scarica prog.txt (eventi)
print(f"Scarico eventi da: {url_events}")
response_events = requests.get(url_events)
if response_events.status_code != 200:
    print(f"Errore nel download di prog.txt: HTTP {response_events.status_code}")
    exit(1)
lines_events = response_events.text.strip().splitlines()

# Scarica 247.txt (canali)
print(f"Scarico canali da: {url_channels}")
response_channels = requests.get(url_channels)
if response_channels.status_code != 200:
    print(f"Errore nel download di 247.txt: HTTP {response_channels.status_code}")
    exit(1)
lines_channels = response_channels.text.strip().splitlines()

# Inizia l'HTML
html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Sportzonline - Eventi e Canali</title>
<style>
body { font-family: 'Arial', sans-serif; margin: 0; padding: 0; background-color: #0f0f0f; color: #fff; }
header { background-color: #1c1c1c; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; }
.container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
input[type="text"] { width: 100%%; padding: 12px; margin-bottom: 20px; font-size: 16px; border-radius: 8px; border: none; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
.card { background-color: #1a1a1a; border-radius: 10px; padding: 15px; text-align: center; transition: transform 0.2s, background-color 0.2s; }
.card:hover { transform: translateY(-5px); background-color: #222; }
button { width: 100%%; padding: 10px; font-size: 16px; border: none; border-radius: 8px; cursor: pointer; color: #fff; transition: background-color 0.2s; }
.btn-event { background-color: #ff4d4d; }    /* rosso */
.btn-event:hover { background-color: #ff1a1a; }
.btn-channel { background-color: #00bfff; }  /* azzurro */
.btn-channel:hover { background-color: #0099e6; }
h2 { margin-top: 40px; color: #ccc; border-bottom: 1px solid #333; padding-bottom: 5px; }
.time { font-size: 14px; color: #aaa; margin-bottom: 5px; }
</style>
</head>
<body>
<header>Sportzonline - Eventi e Canali</header>
<div class="container">
<input type="text" id="searchInput" placeholder="Cerca evento o canale...">

<script>
document.addEventListener("DOMContentLoaded", function() {
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', function() {
    const filter = searchInput.value.toLowerCase();
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
      const text = card.textContent.toLowerCase();
      card.style.display = text.includes(filter) ? '' : 'none';
    });
  });
});
</script>
"""

# --- NUOVA SEZIONE EVENTI RAGGRUPPATI ---
html += "<h2>Eventi</h2>\n<div class='grid'>\n"

# 1. Raggruppiamo i link per nome evento
eventi_raggruppati = {}

for line in lines_events:
    line = line.strip()
    if not line or "http" not in line or "|" not in line:
        continue

    left, url = line.split("|", 1)
    name = left.strip().replace('"', "'")
    url = url.strip()
    
    # Gestione orario
    time_str = ""
    display_name = name
    if ":" in name:
        parts = name.split(" ", 1)
        try:
            time_obj = datetime.strptime(parts[0], "%H:%M") + timedelta(hours=1)
            time_str = time_obj.strftime("%H:%M")
            display_name = parts[1] if len(parts) > 1 else ""
        except:
            pass

    # Usiamo il nome del match come chiave per raggruppare
    if display_name not in eventi_raggruppati:
        eventi_raggruppati[display_name] = {'ora': time_str, 'links': []}
    
    eventi_raggruppati[display_name]['links'].append(url)

# 2. Generiamo l'HTML usando i dati raggruppati
for nome_match, dati in eventi_raggruppati.items():
    html += f"<div class='card'>\n"
    if dati['ora']:
        html += f"<div class='time'>{dati['ora']}</div>\n"
    html += f"<div style='margin-bottom:10px; font-weight:bold;'>{nome_match}</div>\n"
    
    # Creiamo un bottone per ogni link trovato per questo match
    for i, link in enumerate(dati['links'], 1):
        html += f"<button class='btn-event' style='margin-bottom:5px;' onclick=\"window.open('{link}', '_blank')\">Link {i}</button>\n"
    
    html += "</div>\n"

html += "</div>\n"
# --- FINE NUOVA SEZIONE EVENTI ---
# Sezione Canali
html += "<h2>Canali TV</h2>\n<div class='grid'>\n"

for line in lines_channels:
    line = line.strip()
    if not line or "http" not in line:
        continue

    if "-" in line:
        left, right = line.split("-", 1)
        name = left.strip().replace('"', "'")
        url = right.strip()
        # Aggiorna il dominio al link reale
        if url.startswith("http"):
            url = url.replace("sportzonline.site", "sportsonline.cv")
        html += f"<div class='card'>\n"
        html += f"<button class='btn-channel' onclick=\"window.open('{url}', '_blank')\">{name}</button>\n"
        html += "</div>\n"
    else:
        print(f"Riga canale ignorata: {line}")

html += "</div>\n</div></body></html>"

# Scrivi su file
with open("sportzonline_lista.html", "w", encoding="utf-8") as f:
    f.write(html)

print("File 'sportzonline_lista.html' creato con successo!")
