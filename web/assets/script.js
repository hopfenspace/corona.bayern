var mymap = L.map('coronamap', {
    minZoom: 7,
    maxZoom: 12,
    maxBounds: [
        [50.608, 8.701],
        [47.223, 14.150],
    ],
}).setView([48.834, 11.245], 8);

L.tileLayer('https://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png ', {
    subdomains: 'abc',
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, '
        + '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, '
        + 'Kontakt: info@corona.bayern',
}).addTo(mymap);

function render(data)
{
    document.getElementById("timestamp").innerText = data.timestamp;
    document.getElementById("source").href = data.source;
    document.getElementById("sickSum").innerText = data.sickSum;

    for(var i = 0; i < data.entries.length; i++) {
        var entry = data.entries[i];

        if(entry.sick == 0)
        {
            var color = "#0180b2";
            var radius = Math.sqrt(1 * 3e6 / Math.PI);;
        }
        else
        {
            var color = "red";
            var radius = Math.sqrt(entry.sick * 3e6 / Math.PI);
        }

        L.circle([entry.lat, entry.lng], {radius: radius, color: color, fillOpacity: 0.7})
            .addTo(mymap)
            .bindPopup("<b>" + entry.name + "</b>" +
                "<br />Infiziert: " + entry.sick +
                "<br />Geheilt: " + entry.cured +
                "<br />Todesfälle: " + entry.deaths
            );
    }
}

fetch('data.json', {cache: "no-cache"})
    .then(res => res.json())
    .then(data => render(data));