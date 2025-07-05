import requests

# URL dei due file
url_events = "https://sportsonline.ci/prog.txt"
url_channels = "https://sportzonline.si/247.txt"

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
<title>Eventi e Canali Sportzonline</title>
<style>
body { font-family: sans-serif; margin: 20px; }
input[type="text"] { width: 100%%; padding: 10px; margin-bottom: 20px; font-size: 16px; }

h1 { margin-bottom: 20px; }
h2 { margin-top: 40px; color: #333; }
div { margin-bottom: 10px; }

button {
  margin: 3px;
  padding: 6px 10px;
  font-size: 14px;
  display: inline-block;
  border: none;
  border-radius: 5px;
  color: white;
  cursor: pointer;
}

.btn-event { background-color: #2196F3; }    /* blu */
.btn-channel { background-color: #4CAF50; }  /* verde */
</style>
</head>
<body>
<h1>Eventi e Canali - Sportzonline</h1>

<input type="text" id="searchInput" placeholder="Cerca evento o canale...">

<script>
document.addEventListener("DOMContentLoaded", function() {
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', function() {
    const filter = searchInput.value.toLowerCase();
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
      const text = button.textContent.toLowerCase();
      button.parentElement.style.display = text.includes(filter) ? '' : 'none';
    });
  });
});
</script>
"""

# Sezione Eventi
html += "<h2>Eventi</h2>\n"

for line in lines_events:
    line = line.strip()
    if not line or "http" not in line:
        continue  # Salta righe vuote o righe senza URL

    if "|" in line:
        left, right = line.split("|", 1)
        name = left.strip().replace('"', "'")
        url = right.strip()
        html += f'<div>\n'
        html += f'<button class="btn-event" onclick="window.open(\'{url}\', \'_blank\')">{name}</button>\n'
        html += f'</div>\n'
    else:
        print(f"Riga evento ignorata: {line}")

# Sezione Canali
html += "<h2>Canali</h2>\n"

for line in lines_channels:
    line = line.strip()
    if not line or "http" not in line:
        continue  # Salta righe vuote o righe senza URL

    if "-" in line:
        left, right = line.split("-", 1)
        name = left.strip().replace('"', "'")
        url = right.strip()
        html += f'<div>\n'
        html += f'<button class="btn-channel" onclick="window.open(\'{url}\', \'_blank\')">{name}</button>\n'
        html += f'</div>\n'
    else:
        print(f"Riga canale ignorata: {line}")

html += "</body></html>"

# Scrivi su file
with open("sportzonline_lista.html", "w", encoding="utf-8") as f:
    f.write(html)

print("File 'sportzonline_lista.html' creato con successo!")
