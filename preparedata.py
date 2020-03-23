import os, re, json, demjson, dateutil.parser, urllib.request

# you can obtain the county-centres-bavaria.json file by running the following
#  query on overpass-turbo.eu and export the result as GeoJSON
'''
(area["ISO3166-2"="DE-BY"];)->.bayern;
rel["boundary"="administrative"]["admin_level"="6"](area.bayern)->.landkreise;
node(r.landkreise);
out;
.landkreise out;
'''

with open("county-centres-bavaria.json", "r", encoding="utf-8") as fd:
    counties = json.load(fd)

url = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=BL_ID%3D9&geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&returnZ=false&returnM=false&returnExceededLimitFeatures=true&sqlFormat=none&f=json"
htmlSrc = urllib.request.urlopen(url).read().decode("utf-8")
allData = json.loads(htmlSrc)["features"]

source = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_Landkreisdaten/FeatureServer"
timestamp = allData[0]["attributes"]["last_update"]

data = {}
for entry in allData:
    entry = entry["attributes"]
    key = entry["RS"]
    data[key] = entry

bavariaData = []
sickSum = 0
deathSum = 0

for centre in counties["features"]:
    props = centre["properties"]

    people = 0
    sick = 0
    deaths = 0
    names = []

    for county in props["@relations"]:
        key = county["reltags"]["de:amtlicher_gemeindeschluessel"][0 : 5]
        names.append(county["reltags"]["name"])
        if key in data:
            people += data[key]["EWZ"]
            sick += data[key]["cases"]
            deaths += data[key]["deaths"]

        del data[key]

    sickSum += sick
    deathSum += deaths

    pos = centre["geometry"]["coordinates"]
    bavariaData.append({
        "name": " & ".join(names),
        "people": people,
        "sick": sick,
        "deaths": deaths,
        "lng": pos[0],
        "lat": pos[1],
    })

bavariaData = {
    "source": source,
    "timestamp": timestamp,
    "sickSum": sickSum,
    "deathSum": deathSum,
    "entries": bavariaData,
}

timestamp = dateutil.parser.parse(timestamp).isoformat()
with open("web/history/{}.json".format(timestamp), "w+", encoding="utf-8") as fd:
    json.dump(bavariaData, fd, indent=4)

os.unlink("web/data.json")
os.symlink("history/{}.json".format(timestamp), "web/data.json")
