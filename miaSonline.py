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
    print("Errore download prog.txt")
    exit()

lines_events = response_events.text.strip().splitlines()

print(f"Scarico canali da: {url_channels}")
response_channels = requests.get(url_channels)

if response_channels.status_code != 200:
    print("Errore download 247.txt")
    exit()

lines_channels = response_channels.text.strip().splitlines()

# ================= PEPPER =================

print("Scarico Pepperlive...")

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://pepperlive.info/"
}

response_pepper = requests.get(url_pepper, headers=headers)

pepper_html = ""
if response_pepper.status_code == 200:
    pepper_html = response_pepper.text

pepper_events = []

if pepper_html:

    cards = re.findall(
        r'<div class="match-card.*?">(.*?)</div>\s*</div>',
        pepper_html,
        re.S
    )

    for card in cards:

        time_match = re.search(r'class="ora-txt".*?>(.*?)<', card)

        hour = ""

        if time_match:
            hour = time_match.group(1).strip()

            try:
                t = datetime.strptime(hour,"%H:%M") + timedelta(hours=1)
                hour = t.strftime("%H:%M")
            except:
                pass

        teams_match = re.search(r'class="teams-box">(.*?)</div>', card, re.S)

        if not teams_match:
            continue

        match_name = teams_match.group(1)
        match_name = re.sub('<.*?>','',match_name)
        match_name = match_name.replace("VS","vs").strip()

        channels = re.findall(
            r'href="(live\.php\?ch=[^"]+)".*?>(.*?)<',
            card
        )

        final_links = []

        for link,label in channels:

            match_id = re.search(r'(\d+)',link)

            if match_id:
                channel_id = match_id.group(1)
                url = f"https://pepperlive.info/sportp.php?id={channel_id}"
            else:
                url = "https://pepperlive.info/"+link

            final_links.append((label.upper(),url))

        if final_links:

            pepper_events.append({
                "match":match_name,
                "time":hour,
                "links":final_links
            })

# ================= HTML =================

html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Sportzonline</title>

<style>

body{
font-family:Segoe UI;
background:#0a0b10;
color:white;
margin:0;
}

header{
background:#111;
padding:25px;
text-align:center;
font-size:26px;
font-weight:bold;
}

.container{
max-width:1200px;
margin:auto;
padding:20px;
}

input{
width:100%;
padding:14px;
margin-bottom:25px;
border-radius:10px;
border:none;
background:#222;
color:white;
}

.grid{
display:grid;
grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
gap:18px;
}

.card{
background:#1a1a2e;
padding:18px;
border-radius:12px;
text-align:center;
}

button{
width:100%;
padding:10px;
margin-top:6px;
border:none;
border-radius:6px;
font-weight:bold;
cursor:pointer;
}

.btn-event{
background:#3a7bd5;
color:white;
}

.btn-channel{
background:#00f2fe;
color:black;
}

.time{
color:#00d2ff;
font-weight:bold;
margin-bottom:6px;
}

h2{
margin-top:40px;
}

</style>

<script>

function toggleSection(id){

var el = document.getElementById(id);

if(el.style.display === "none"){
el.style.display="block";
}else{
el.style.display="none";
}

}

document.addEventListener("DOMContentLoaded",function(){

var input=document.getElementById("searchInput");

input.addEventListener("input",function(){

var filter=input.value.toLowerCase();
var cards=document.querySelectorAll(".card");

cards.forEach(function(card){

var text=card.textContent.toLowerCase();

if(text.includes(filter)){
card.style.display="";
}else{
card.style.display="none";
}

});

});

});

</script>

</head>

<body>

<header>Sportzonline</header>

<div class="container">

<input type="text" id="searchInput" placeholder="Cerca evento o canale">

<div style="margin-bottom:20px;">

<button onclick="toggleSection('sport_section')">Sportsonline</button>

<button onclick="toggleSection('pepper_section')">Pepperlive</button>

</div>
"""

# ================= EVENTI =================

html += "<div id='sport_section' style='display:none'>"
html += "<h2>Eventi</h2><div class='grid'>"

eventi = {}

for line in lines_events:

    if "|" not in line:
        continue

    left,url=line.split("|",1)

    name=left.strip()
    url=url.strip()

    time=""
    display=name

    if ":" in name:

        parts=name.split(" ",1)

        try:

            t=datetime.strptime(parts[0],"%H:%M")+timedelta(hours=1)
            time=t.strftime("%H:%M")

            if len(parts)>1:
                display=parts[1]

        except:
            pass

    if display not in eventi:
        eventi[display]={"ora":time,"links":[]}

    eventi[display]["links"].append(url)

for match,data in eventi.items():

    html+="<div class='card'>"

    if data["ora"]:
        html+=f"<div class='time'>{data['ora']}</div>"

    html+=f"<div><b>{match}</b></div>"

    for i,l in enumerate(data["links"],1):
        html+=f"<button class='btn-event' onclick=\"window.open('{l}')\">Link {i}</button>"

    html+="</div>"

html+="</div></div>"

# ================= CANALI =================

html+="<h2>Canali TV</h2><div class='grid'>"

for line in lines_channels:

    if "-" not in line:
        continue

    left,right=line.split("-",1)

    name=left.strip()
    url=right.strip()

    url=url.replace("sportzonline.site","sportsonline.cv")

    html+="<div class='card'>"
    html+=f"<button class='btn-channel' onclick=\"window.open('{url}')\">{name}</button>"
    html+="</div>"

html+="</div>"

# ================= PEPPER =================

html += "<div id='pepper_section' style='display:none'>"
html += "<h2>Pepperlive</h2><div class='grid'>"

for ev in pepper_events:

    html+="<div class='card'>"

    if ev["time"]:
        html+=f"<div class='time'>{ev['time']}</div>"

    html+=f"<div><b>{ev['match']}</b></div>"

    for label,link in ev["links"]:
        html+=f"<button class='btn-event' onclick=\"window.open('{link}')\">{label}</button>"

    html+="</div>"

html+="</div></div>"

html+="</div></body></html>"

# ================= SAVE =================

with open("sportzonline_lista.html","w",encoding="utf8") as f:
    f.write(html)

print("HTML creato!")
