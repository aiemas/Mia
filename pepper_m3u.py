import requests
import re

base = "https://pepperlive.info"

channels = range(1,120)

headers = {
"User-Agent":"Mozilla/5.0"
}

m3u = "#EXTM3U\n"

for ch in channels:

    url = f"{base}/live.php?ch={ch}"

    try:

        r = requests.get(url,headers=headers,timeout=10)

        if r.status_code != 200:
            continue

        source = r.text

        m3u8 = re.search(r'https://[^"]+\.m3u8[^"]*',source)

        if m3u8:

            stream = m3u8.group(0)

            m3u += f'#EXTINF:-1,Pepper {ch}\n'
            m3u += stream + "\n"

            print("trovato",ch)

    except:
        pass

with open("cazzimiei.m3u","w") as f:
    f.write(m3u)
