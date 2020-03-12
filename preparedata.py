import re, json, demjson, urllib.request

with open("counties-bavaria.json", "r") as fd:
    counties = json.load(fd)

url = "https://www.lgl.bayern.de/gesundheit/infektionsschutz/infektionskrankheiten_a_z/coronavirus/karte_coronavirus/index.htm"
htmlSrc = urllib.request.urlopen(url).read().decode("utf-8")

timestamp = re.search("Stand: (.*?) Uhr", htmlSrc).group(1)

data = re.search("areas\s*:\s*(\\{.*?\\})\\);", htmlSrc.replace("\r\n", ""), re.UNICODE)
data = data.group(1)[ : -1]
data = demjson.decode(data)

bavariaData = []

for county in counties["features"]:
    props = county["properties"]
    dataKey =  "lkr_" + props["de:amtlicher_gemeindeschluessel"][2 :]
    if dataKey in data:
        sick = data[dataKey]["value"]
    else:
        sick = 0

    pos = county["geometry"]["coordinates"]
    bavariaData.append({
        "name": props["name"],
		"sick": sick,
		"cured": 0, # TODO, currently 0 in bavaria, will lgl.bayern.de provide this?
		"deaths": 0, # TODO, currently 0 in bavaria, will lgl.bayern.de provide this?
		"lng": pos[0],
		"lat": pos[1],
    })

bavariaData = {
    "source": url,
    "timestamp": timestamp,
    "entries": bavariaData,
}

with open("web/data.json", "w+") as fd:
	json.dump(bavariaData, fd, indent=4)
