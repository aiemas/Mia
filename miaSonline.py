import requests
from datetime import datetime, timedelta
import re

# URL del file eventi
url_events = "https://sportsonline.ci/prog.txt"

# Scarica il file
print(f"Scarico eventi da: {url_events}")
response = requests.get(url_events)
if response.status_code != 200:
    print(f"Errore nel download: HTTP {response.status_code}")
    exit(1)

lines = response.text.strip().splitlines()

# -----------------------------
# Step 1: Leggi legenda canali
# -----------------------------
channel_lang = {}
for line in lines:
    line = line.strip()
    # cerca linee tipo "HD1 ENGLISH" o "BR2 BRAZILIAN"
    match = re.match(r'^(HD|BR|PT)(\d+)\s+([A-Z &]+)', line)
    if match:
        prefix, num, lang = match.groups()
        key = f"{prefix}{num}".lower()  # es. hd7
        channel_lang[key] = lang.title()  # ENGLISH -> English

# -----------------------------
# Step 2: Raggruppa partite
# -----------------------------
matches = {}
for line in lines:
    line = line.strip()
    if not line or "https://sportsonline.cv/channels/" not in line:
        continue

    try:
        time_part, rest = line.split("   ", 1)  # triplo spazio
        title, url = rest.rsplit(" | ", 1)

        # aggiusta orario +1
        try:
            time_obj = datetime.strptime(time_part.strip(), "%H:%M") + timedelta(hours=1)
            time_str = time_obj.strftime("%H:%M")
        except:
            time_str = time_part.strip()

        # correggi dominio sempre su .cv
        url = url.replace("https://sportsonline.sn/channels/", "https://sportsonline.cv/channels/")

        # chiave partita
        key = title.strip()
        if key not in matches:
            matches[key] = {"time": time_str, "urls": []}
        matches[key]["urls"].append(url)
    except:
        print(f"Riga ignorata: {line}")

# -----------------------------
# Step 3: Costruisci HTML
# -----------------------------
html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Sportzonline - Eventi e Canali</title>
<style>
body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #121212; color: #fff; }
header { background-color: #1f1f1f; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; }
.container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
input[type="text"] { width: 100%%; padding: 12px; margin-bottom: 20px; font-size: 16px; border-radius: 8px; border: none; }
.match { background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
.match:hover { background-color: #2c2c2c; }
.match-time { font-size: 16px; color: #bbb; margin-bottom: 5px; }
.match-title { font-size: 18px; margin-bottom: 8px; }
.channel-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 5px; }
button { padding: 8px 12px; border-radius: 6px; border: none; cursor: pointer; color: #fff; font-size: 14px; transition: 0.2s; }
.btn-channel { background-color: #00bfff; }
.btn-channel:hover { background-color: #0099e6; }
</style>
</head>
<body>
<header>Sportzonline - Eventi e Canali</header>
<div class="container">
<input type="text" id="searchInput" placeholder="Cerca partita o canale...">

<script>
document.addEventListener("DOMContentLoaded", function() {
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', function() {
    const filter = searchInput.value.toLowerCase();
    const matches = document.querySelectorAll('.match');
    matches.forEach(match => {
      match.style.display = match.textContent.toLowerCase().includes(filter) ? '' : 'none';
    });
  });
});
</script>
"""

# Costruisci le partite con i pulsanti lingua
for title, info in matches.items():
    html += f'<div class="match">\n'
    html += f'<div class="match-time">{info["time"]}</div>\n'
    html += f'<div class="match-title">{title}</div>\n'
    html += '<div class="channel-row">\n'
    for url in info["urls"]:
        # estrai id canale dal link
        ch_id_match = re.search(r'/channels/[^/]+/([a-z0-9]+)\.php', url)
        if ch_id_match:
            ch_id = ch_id_match.group(1).lower()  # es. hd7
            lang = channel_lang.get(ch_id, "Unknown")
        else:
            lang = "Unknown"
        html += f'<button class="btn-channel" onclick="window.open(\'{url}\', \'_blank\')">{lang}</button>\n'
    html += '</div></div>\n'

html += "</div></body></html>"

# Scrivi file
with open("sportzonline_lista.html", "w", encoding="utf-8") as f:
    f.write(html)

print("File 'sportzonline_lista.html' creato con successo!")
