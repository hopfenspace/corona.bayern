import json

with open("rawdata.json", "r") as fd:
	data = fd.read().replace("\\\\", "\\")
	data = json.loads(data)

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
		"lat": loc["lat"],
		"lng": loc["lng"],
	})

with open("data.json", "w+") as fd:
	json.dump(bavariaData, fd)
