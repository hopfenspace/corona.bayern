import re, json, urllib.request, dateutil.parser as dateparser

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

	changed = dateparser.parse(entry["datum"][7 : ].replace("Uhr", ""))

	bavariaData.append({
		"name": entry["title"],
		"sick": entry["infizierte"] or "0",
		"cured": entry["geheilte"] or "0",
		"deaths": entry["todesfaelle"] or "0",
		"updated": changed.strftime("%d.%m.%Y %H:%M"),
		"lat": loc["lat"],
		"lng": loc["lng"],
	})

with open("data.json", "w+") as fd:
	json.dump(bavariaData, fd, indent=4)
