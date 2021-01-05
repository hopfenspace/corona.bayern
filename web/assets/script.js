var mymap = L.map('coronamap', {
    minZoom: 6,
    maxZoom: 12,
    maxBounds: [
        [51, 8],
        [46, 15.5],
    ],
}).setView([48.834, 11.245], 8);

L.tileLayer('https://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png ', {
    subdomains: 'abc',
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, '
        + '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, '
        + 'Kontakt: info@corona.bayern',
}).addTo(mymap);

function render(data, counties)
{
    document.getElementById("timestamp").innerText = data.timestamp;
    document.getElementById("source").href = data.source;
    document.getElementById("sickSum").innerText = data.sickSum;
    document.getElementById("deathSum").innerText = data.deathSum;
    document.getElementById("deathRate").innerText = Math.round(data.deathSum * 10000 / data.sickSum) / 100;
    var usePercent = document.location.search === "?percent";

    data.entries.sort((a, b) => b.sick - a.sick);

    var maxEntry = 0;
    var minEntry = Number.MAX_SAFE_INTEGER;
    if(usePercent)
    {
        data.entries.forEach(entry => {
            var percent = Math.round(entry.sick * 10000 / entry.people) / 100;
            if(percent > maxEntry)
                maxEntry = percent;
            if(percent < minEntry)
                minEntry = percent;
        });
    }

    for(var i = 0; i < data.entries.length; i++)
    {
        var entry = data.entries[i];
        var percent = Math.round(entry.sick * 10000 / entry.people) / 100;
        var deathRate = Math.round(entry.deaths * 10000 / entry.sick) / 100;
        var incidence = Math.round(entry.incidence * 100) / 100;

        var county = counties.features.find(x => x.properties["de:amtlicher_gemeindeschluessel"] === entry.key);
        if(!county)
        {
            console.error("could not find polygon for ", entry, county);
            continue;
        }

        var coordinates = [];
        if(county.geometry.type === "MultiPolygon")
        {
            county.geometry.coordinates.map(x => coordinates.push(x[0]));
        }
        else if(county.geometry.type === "Polygon")
        {
            coordinates.push(county.geometry.coordinates[0]);
        }
        else
        {
            console.error("unknown geometry shape ", county);
            continue;
        }

        coordinates = coordinates.map(x => x.map(([lon, lat]) => [lat, lon]));

        console.log(entry.name, county.geometry.type, coordinates);

        var color;
        var fillOpacity = 0.3;
        if(entry.sick == 0)
        {
            color = "#0180b2";
        }
        else if(usePercent)
        {
            color = "red";
            fillOpacity = 0.1 + (percent - minEntry) / (maxEntry - minEntry) * 0.9;
        }
        else // incidence
        {
            if(entry.incidence <= 35)
                color = "green";
            else if(entry.incidence <= 50)
                color = "orange";
            else if(entry.incidence <= 100)
                color = "red";
            else if(entry.incidence <= 200)
                color = "darkred";
            else
                color = "purple";
        }

        var text = "<b>" + entry.name + "</b>"
            + "<br />Inzidenzzahl: " + incidence
            + "<br />Infiziert: " + entry.sick
            + "<br />Tote: " + entry.deaths
            + "<br />Durchseuchung: " + percent + "%"
            + "<br />Sterberate: " + deathRate + "%";
        coordinates.forEach(poly => {
            L.polygon(poly, { color, fillOpacity })
                .addTo(mymap)
                .bindTooltip(text, {sticky: true, direction: "top"});
        });
    }
}

Promise.all([
    fetch('county-polygons.json')
        .then(res => res.json()),
    fetch('data.json', {cache: "no-cache"})
        .then(res => res.json())
])
    .then(([counties, data]) => render(data, counties))
