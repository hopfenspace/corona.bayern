#!/usr/bin/python3

import os, re, json, demjson, datetime, urllib.request

# you can obtain the county-centres-bavaria.json file by running the following
#  query on overpass-turbo.eu and export the result as GeoJSON
'''
(area["ISO3166-2"="DE-BY"];)->.bayern;
rel["boundary"="administrative"]["admin_level"="6"](area.bayern)->.landkreise;
node(r.landkreise);
out;
.landkreise out;
'''

# you can obtain the county-boundaries-bavaria.json file by running the following
#  query on overpass-turbo.eu and export the result as GeoJSON and simplify using
#  mapshaper.org
'''
area(3602145268);
rel
  [admin_level~"6"]
  (area);
out body;
>;
out skel qt;
'''


with open("county-polygons-bavaria.json", "r", encoding="utf-8") as fd:
    counties = json.load(fd)

url = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=BL_ID%3D9&geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&returnZ=false&returnM=false&returnExceededLimitFeatures=true&sqlFormat=none&f=json"
htmlSrc = urllib.request.urlopen(url).read().decode("utf-8")
allData = json.loads(htmlSrc)["features"]

source = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_Landkreisdaten/FeatureServer"
timestamp = allData[0]["attributes"]["last_update"].replace("Uhr", "").strip()

data = {}
for entry in allData:
    entry = entry["attributes"]
    key = entry["RS"]
    data[key] = entry

bavariaData = []
sickSum = 0
deathSum = 0

for county in counties["features"]:
    props = county["properties"]
    key = props["de:amtlicher_gemeindeschluessel"]
    dataKey = key[0 : 5]

    name = props["name"]
    people = data[dataKey]["EWZ"]
    sick = data[dataKey]["cases"]
    deaths = data[dataKey]["deaths"]
    incidence = data[dataKey]["cases7_per_100k"]

    sickSum += sick
    deathSum += deaths

    bavariaData.append({
        "key": key,
        "name": name,
        "incidence": incidence,
        "people": people,
        "sick": sick,
        "deaths": deaths,
    })

bavariaData = {
    "source": source,
    "timestamp": timestamp,
    "sickSum": sickSum,
    "deathSum": deathSum,
    "entries": bavariaData,
}

timestamp = datetime.datetime.strptime(timestamp, "%d.%m.%Y, %H:%M").isoformat()
with open("web/history/{}.json".format(timestamp), "w+", encoding="utf-8") as fd:
    json.dump(bavariaData, fd, indent=4)

os.unlink("web/data.json")
os.symlink("history/{}.json".format(timestamp), "web/data.json")
