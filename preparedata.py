import re, json, demjson, urllib.request

# you can obtain the county-centres-bavaria.json file by running the following
#  query on overpass-turbo.eu and export the result as GeoJSON
'''
(area["ISO3166-2"="DE-BY"];)->.bayern;
rel["boundary"="administrative"]["admin_level"="6"](area.bayern)->.landkreise;
node(r.landkreise);
out;
.landkreise out;
'''

with open("county-centres-bavaria.json", "r") as fd:
    counties = json.load(fd)

url = "https://www.lgl.bayern.de/gesundheit/infektionsschutz/infektionskrankheiten_a_z/coronavirus/karte_coronavirus/index.htm"
htmlSrc = urllib.request.urlopen(url).read().decode("utf-8")

timestamp = re.search("Stand: (.*?) Uhr", htmlSrc).group(1)

data = re.search("areas\\s*:\\s*(\\{.*?\\})\\);", htmlSrc.replace("\r\n", ""), re.UNICODE)
data = data.group(1)[ : -1]
data = demjson.decode(data)

bavariaData = []
sickSum = 0

for centre in counties["features"]:
    props = centre["properties"]

    sick = 0
    names = []

    for county in props["@relations"]:
        dataKey =  "lkr_" + county["reltags"]["de:amtlicher_gemeindeschluessel"][2 : 5]
        names.append(county["reltags"]["name"])
        if dataKey in data:
            sick += data[dataKey]["value"]

    sickSum += sick

    pos = centre["geometry"]["coordinates"]
    bavariaData.append({
        "name": " & ".join(names),
        "sick": sick,
        "cured": 0, # TODO, currently 0 in bavaria, will lgl.bayern.de provide this?
        "deaths": 0, # TODO, currently 0 in bavaria, will lgl.bayern.de provide this?
        "lng": pos[0],
        "lat": pos[1],
    })

bavariaData = {
    "source": url,
    "timestamp": timestamp,
    "sickSum": sickSum,
    "entries": bavariaData,
}

with open("web/data.json", "w+") as fd:
	json.dump(bavariaData, fd, indent=4)
