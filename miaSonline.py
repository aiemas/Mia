import requests
import re
from datetime import datetime, timedelta


# URL
url_events = "https://sportsonline.ci/prog.txt"
url_channels = "https://sportzonline.site/247.txt"
url_pepper = "https://pepperlive.info/"


# ================== DOWNLOAD ==================

print("Scarico eventi...")
r_events = requests.get(url_events)
lines_events = r_events.text.strip().splitlines()


print("Scarico canali...")
r_channels = requests.get(url_channels)
lines_channels = r_channels.text.strip().splitlines()


print("Scarico Pepperlive...")
r_pepper = requests.get(url_pepper)
pepper_html = r_pepper.text if r_pepper.status_code == 200 else ""


# ================== PARSE PEPPER ==================

pepper_events = []

if pepper_html:

    blocks = re.findall(
        r'<div class="kode_ticket_text">(.*?)</div>\s*<div class="ticket_btn">(.*?)</div>',
        pepper_html,
        re.S
    )

    for info, links in blocks:

        teams = re.findall(r'<h2>(.*?)</h2>', info)
        time = re.search(r'<p>(.*?)</p>', info)

        if len(teams) >= 2 and time:

            team1 = teams[0].strip().title()
            team2 = teams[1].strip().title()
            hour = time.group(1).strip()

            # +1 ora
            try:
                t = datetime.strptime(hour, "%H:%M") + timedelta(hours=1)
                hour = t.strftime("%H:%M")
            except:
                pass

            channels = re.findall(
                r'href="(sportp\.php\?id=[^"]+)".*?>(.*?)<',
                links
            )

            final_links = []

            for link, lang in channels:
                url = "https://pepperlive.info/" + link
                final_links.append((lang.upper(), url))

            pepper_events.append({
                "match": f"{team1} vs {team2}",
                "time": hour,
                "links": final_links
            })


# ================== HTML ==================

html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Sportzonline - Eventi e Canali</title>

<style>
body { background:#0a0b10; color:#fff; font-family:Segoe UI; margin:0 }
header { background:#0f3460; padding:25px; text-align:center; font-size:26px; }
.container { max-width:1200px; margin:auto; padding:20px }
input { width:100%%; padding:12px; margin-bottom:25px }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:20px }
.card { background:#1a1a2e; padding:20px; border-radius:12px; text-align:center }
button { width:100%%; padding:10px; margin:4px 0; border:0; border-radius:6px; cursor:pointer }
.btn-event { background:#00d2ff }
.btn-channel { background:#4facfe }
.time { color:#00d2ff; font-weight:bold; margin-bottom:6px }
h2 { margin-top:40px; border-left:4px solid #00d2ff; padding-left:10px }
</style>

</head>

<body>

<header>Sportzonline - Eventi e Canali</header>

<div class="container">

<input id="searchInput" placeholder="Cerca...">

<script>
document.getElementById("searchInput").addEventListener("input",function(){
 let f=this.value.toLowerCase();
 document.querySelectorAll(".card").forEach(c=>{
  c.style.display=c.textContent.toLowerCase().includes(f)?"":"none";
 });
});
</script>
"""


# ================== EVENTI SPORTSONLINE ==================

html += "<h2>Eventi</h2><div class='grid'>"

eventi = {}

for line in lines_events:

    if "|" not in line:
        continue

    name, url = line.split("|",1)

    name = name.strip()
    url = url.strip()

    time = ""
    title = name

    if ":" in name:

        p = name.split(" ",1)

        try:
            t = datetime.strptime(p[0],"%H:%M")+timedelta(hours=1)
            time = t.strftime("%H:%M")
            title = p[1]
        except:
            pass


    if title not in eventi:
        eventi[title]={"time":time,"links":[]}

    eventi[title]["links"].append(url)



for k,v in eventi.items():

    html += "<div class='card'>"

    if v["time"]:
        html += f"<div class='time'>{v['time']}</div>"

    html += f"<b>{k}</b><br>"

    for i,l in enumerate(v["links"],1):
        html += f"<button class='btn-event' onclick=\"open('{l}')\">Link {i}</button>"

    html += "</div>"


html += "</div>"


# ================== CANALI ==================

html += "<h2>Canali TV</h2><div class='grid'>"

for line in lines_channels:

    if "-" not in line:
        continue

    n,u = line.split("-",1)

    u = u.strip().replace("sportzonline.site","sportsonline.cv")

    html += "<div class='card'>"
    html += f"<button class='btn-channel' onclick=\"open('{u}')\">{n}</button>"
    html += "</div>"


html += "</div>"


# ================== PEPPERLIVE ==================

if pepper_events:

    html += "<h2>Pepperlive</h2><div class='grid'>"


    for ev in pepper_events:

        html += "<div class='card'>"

        html += f"<div class='time'>{ev['time']}</div>"

        html += f"<b>{ev['match']}</b><br>"

        for lang,link in ev["links"]:

            html += f"<button class='btn-event' onclick=\"open('{link}')\">{lang}</button>"

        html += "</div>"


    html += "</div>"


# ================== FINE ==================

html += "</div></body></html>"


with open("sportzonline_lista.html","w",encoding="utf-8") as f:
    f.write(html)


print("File creato!")
