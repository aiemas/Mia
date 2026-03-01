import requests
import re
from datetime import datetime, timedelta

# URL dei file
url_events = "https://sportsonline.ci/prog.txt"
url_channels = "https://sportzonline.site/247.txt"
url_pepper = "https://pepperlive.info/"

# ================= DOWNLOAD FILE =================

print(f"Scarico eventi da: {url_events}")
response_events = requests.get(url_events)
if response_events.status_code != 200:
    print(f"Errore nel download di prog.txt: HTTP {response_events.status_code}")
    exit(1)
lines_events = response_events.text.strip().splitlines()

print(f"Scarico canali da: {url_channels}")
response_channels = requests.get(url_channels)
if response_channels.status_code != 200:
    print(f"Errore nel download di 247.txt: HTTP {response_channels.status_code}")
    exit(1)
lines_channels = response_channels.text.strip().splitlines()

# Scarica Pepperlive
print("Scarico Pepperlive...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    "Referer": "https://pepperlive.info/"
}

response_pepper = requests.get(url_pepper, headers=headers, timeout=15)

pepper_html = ""
if response_pepper.status_code == 200:
    pepper_html = response_pepper.text
else:
    print("Pepper non risponde correttamente:", response_pepper.status_code)


# ================= PARSE PEPPER NUOVA STRUTTURA =================

pepper_events = []

if pepper_html:

    cards = re.findall(
        r'<div class="match-card.*?">(.*?)</div>\s*</div>',
        pepper_html,
        re.S
    )

    for card in cards:

        # ORA
        time_match = re.search(r'class="ora-txt".*?>(.*?)<', card)
        hour = ""
        if time_match:
            hour = time_match.group(1).strip()
            try:
                t = datetime.strptime(hour, "%H:%M") + timedelta(hours=1)
                hour = t.strftime("%H:%M")
            except:
                pass

        # MATCH
        teams_match = re.search(r'class="teams-box">(.*?)</div>', card, re.S)
        if not teams_match:
            continue

        match_name = teams_match.group(1)
        match_name = re.sub('<.*?>', '', match_name)  # rimuove span VS
        match_name = match_name.replace("VS", "vs").strip()

        # LINK
        channels = re.findall(
            r'href="(live\.php\?ch=[^"]+)".*?>(.*?)<',
            card
        )

        if not channels:
            continue

        final_links = []

        for link, label in channels:

            # Trasforma live.php?ch=7 -> sportp.php?id=7
            if link.startswith("live.php?ch="):
                channel_id = link.split("live.php?ch=")[1]
                new_link = f"sportp.php?id={channel_id}"
                url = "https://pepperlive.info/" + new_link
            else:
                # Non toccare altri link (warp, premium, ecc.)
                url = "https://pepperlive.info/" + link

            final_links.append((label.upper(), url))

        pepper_events.append({
            "match": match_name,
            "time": hour,
            "links": final_links
        })


# ================= HTML =================

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
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }
.card { background: #1a1a2e; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #252545; }
button { width: 100%%; padding: 12px; font-size: 14px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; color: #fff; }
.btn-event { background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); margin-top: 8px; }
.btn-channel { background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); color: #000; }
h2 { margin-top: 50px; color: #00d2ff; font-size: 22px; border-left: 5px solid #00d2ff; padding-left: 15px; }
.time { font-size: 16px; color: #00d2ff; font-weight: bold; margin-bottom: 8px; font-family: 'Courier New', monospace; }
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

# ================= EVENTI SPORTSONLINE =================

html += "<h2>Eventi</h2>\n<div class='grid'>\n"

eventi_raggruppati = {}

for line in lines_events:
    line = line.strip()
    if not line or "http" not in line or "|" not in line:
        continue

    left, url = line.split("|", 1)
    name = left.strip().replace('"', "'")
    url = url.strip()

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

    if display_name not in eventi_raggruppati:
        eventi_raggruppati[display_name] = {'ora': time_str, 'links': []}

    eventi_raggruppati[display_name]['links'].append(url)


for nome_match, dati in eventi_raggruppati.items():

    html += "<div class='card'>\n"

    if dati['ora']:
        html += f"<div class='time'>{dati['ora']}</div>\n"

    html += f"<div style='margin-bottom:10px; font-weight:bold;'>{nome_match}</div>\n"

    for i, link in enumerate(dati['links'], 1):
        html += f"<button class='btn-event' onclick=\"window.open('{link}', '_blank')\">Link {i}</button>\n"

    html += "</div>\n"

html += "</div>\n"


# ================= CANALI =================

html += "<h2>Canali TV</h2>\n<div class='grid'>\n"

for line in lines_channels:

    line = line.strip()

    if not line or "http" not in line:
        continue

    if "-" in line:

        left, right = line.split("-", 1)

        name = left.strip().replace('"', "'")
        url = right.strip()

        if url.startswith("http"):
            url = url.replace("sportzonline.site", "sportsonline.cv")

        html += "<div class='card'>\n"
        html += f"<button class='btn-channel' onclick=\"window.open('{url}', '_blank')\">{name}</button>\n"
        html += "</div>\n"

html += "</div>\n"


# ================= PEPPERLIVE =================

if pepper_events:

    html += "<h2>Pepperlive</h2>\n<div class='grid'>\n"

    for ev in pepper_events:

        html += "<div class='card'>\n"

        if ev['time']:
            html += f"<div class='time'>{ev['time']}</div>\n"

        html += f"<div style='margin-bottom:10px; font-weight:bold;'>{ev['match']}</div>\n"

        for label, link in ev['links']:
            html += f"<button class='btn-event' onclick=\"window.open('{link}', '_blank')\">{label}</button>\n"

        html += "</div>\n"

    html += "</div>\n"

html += "</div></body></html>"

# ================= SCRITTURA FILE =================

with open("sportzonline_lista.html", "w", encoding="utf-8") as f:
    f.write(html)

print("File 'sportzonline_lista.html' creato con successo!")
