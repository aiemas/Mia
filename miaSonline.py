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
body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; background-color: #0a0b10; color: #e0e6ed; }
header { background: linear-gradient(135deg, #16213e 0%, #0f3460 100%); padding: 30px; text-align: center; font-size: 28px; font-weight: 800; letter-spacing: 2px; border-bottom: 3px solid #00d2ff; text-transform: uppercase; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
.container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
input[type="text"] { width: 100%%; padding: 15px; margin-bottom: 30px; font-size: 16px; border-radius: 12px; border: 1px solid #1a1a2e; background-color: #16213e; color: #fff; outline: none; transition: 0.3s; box-sizing: border-box; }
input[type="text"]:focus { border-color: #00d2ff; box-shadow: 0 0 10px rgba(0, 210, 255, 0.3); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }
.card { background: #1a1a2e; border-radius: 15px; padding: 20px; text-align: center; transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); border: 1px solid #252545; }
.card:hover { transform: translateY(-8px); border-color: #00d2ff; box-shadow: 0 10px 20px rgba(0,0,0,0.4); background: #1f1f3d; }
button { width: 100%%; padding: 12px; font-size: 14px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; color: #fff; transition: 0.3s; text-transform: uppercase; }
.btn-event { background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); margin-top: 8px; }
.btn-event:hover { filter: brightness(1.2); box-shadow: 0 4px 12px rgba(0, 210, 255, 0.4); }
.btn-channel { background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); color: #000; }
.btn-channel:hover { filter: brightness(1.1); box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4); }
h2 { margin-top: 50px; color: #00d2ff; font-size: 22px; text-transform: uppercase; letter-spacing: 1px; border-left: 5px solid #00d2ff; padding-left: 15px; }
.time { font-size: 16px; color: #00d2ff; font-weight: bold; margin-bottom: 8px; font-family: 'Courier New', monospace; }
.match-name { color: #ffffff; font-size: 17px; min-height: 40px; display: flex; align-items: center; justify-content: center; }
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
