"""Fetch live data that browsers cannot read directly (no CORS) and write compact JSON for the page."""
import json, urllib.request, time, gzip, os, sys

def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": "wildcams-map (github.com/mmllpp772/wildcams)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        return json.loads(data)

os.makedirs("out", exist_ok=True)
ok = True
# Flights: OpenSky Network state vectors (anonymous access)
try:
    j = get("https://opensky-network.org/api/states/all")
    rows = []
    for s in j.get("states") or []:
        lon, lat = s[5], s[6]
        if lon is None or lat is None or s[8]:   # skip unknown position and aircraft on the ground
            continue
        rows.append([round(lon, 3), round(lat, 3), round(s[10] or 0), round(s[7] or s[13] or 0),
                     (s[1] or "").strip(), s[2] or "", round((s[9] or 0) * 3.6)])
    json.dump({"t": j.get("time") or int(time.time()), "src": "OpenSky Network", "f": rows},
              open("out/flights.json", "w"), separators=(",", ":"), ensure_ascii=False)
    print("flights", len(rows))
except Exception as e:
    print("flights failed", e); ok = False
sys.exit(0 if ok else 1)
