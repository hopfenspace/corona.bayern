var mymap = L.map('coronamap').setView([48.834, 11.245], 8);

L.tileLayer('https://a.tile.openstreetmap.de/{z}/{x}/{y}.png ', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, '
        + '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, '
        + 'Kontakt: info@corona.bayern',
    maxZoom: 18,
}).addTo(mymap);

function render(data)
{
    document.getElementById("timestamp").innerText = data.timestamp;
    document.getElementById("source").href = data.source;

    for(var i = 0; i < data.entries.length; i++) {
        var entry = data.entries[i];

        if(entry.sick == 0)
        {
            var color = "#0180b2";
            var radius = 2000;
        }
        else
        {
            var color = "red";
            var radius = Math.sqrt(entry.sick * 8e6 / Math.PI);
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