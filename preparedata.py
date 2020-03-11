import re, json, datetime, urllib.request

def try_parsing_date(text):
    for fmt in ('Stand: %d.%m.%Y, %H:%M Uhr', 'Stand: %H:%M Uhr, %d.%m.%Y ', 'Stand: %H:%M Uhr, %d.%m.%Y'):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

data = urllib.request.urlopen("https://coronamaps.de/covid-19-coronavirus-live-karte-bayern/").read().decode("utf-8")
data = re.search("var mapsvg_options = (.*?);jQuery", data, re.UNICODE)
data = json.loads(data.group(1))

bavariaData = []

for entry in data["data_db"]["objects"]:
	if entry["regions"][0]["id"] != "DE-BY":
		continue

	loc = entry["location"]
	if type(loc) != dict:
		print(loc)
		continue

	bavariaData.append({
		"name": entry["title"],
		"sick": entry["infizierte"] or "0",
		"cured": entry["geheilte"] or "0",
		"deaths": entry["todesfaelle"] or "0",
		"updated": try_parsing_date(entry["datum"]).strftime("%d.%m.%Y %H:%M"),
		"lat": loc["lat"],
		"lng": loc["lng"],
	})

with open("data.json", "w+") as fd:
	json.dump(bavariaData, fd, indent=4)
