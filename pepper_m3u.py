import requests
import re

base = "https://pepperlive.info"

headers = {
    "User-Agent": "Mozilla/5.0"
}

channels = range(1,150)

streams = {}

for ch in channels:

    url = f"{base}/live.php?ch={ch}"

    try:

        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            continue

        source = r.text

        # trova tutti gli m3u8
        links = re.findall(r'https://[^\'"]+\.m3u8[^\'"]*', source)

        for link in links:

            # nome stream basato su id
            stream_id = re.search(r'/stream/(\d+)/', link)

            if stream_id:
                name = f"Pepper_{stream_id.group(1)}"
            else:
                name = f"Pepper_{ch}"

            streams[name] = link

    except:
        pass


m3u = "#EXTM3U\n"

for name, link in streams.items():

    m3u += f'#EXTINF:-1,{name}\n'
    m3u += link + "\n"


with open("cazzimiei.m3u", "w") as f:
    f.write(m3u)

print("Creati", len(streams), "stream")
