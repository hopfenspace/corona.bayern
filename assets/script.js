var mymap = L.map('coronamap').setView([48.834, 11.245], 8);

L.tileLayer('https://a.tile.openstreetmap.de/{z}/{x}/{y}.png ', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, '
        + '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, '
        + 'Kontakt: info@corona.bayern, '
        + 'Corona Zahlen vom 09.03.2020',
    maxZoom: 18,
}).addTo(mymap);

function render(entries)
{
    for(var i = 0; i < entries.length; i++) {
        var entry = entries[i];
    
        var radius = Math.sqrt(entry.sick * 8e6 / Math.PI);
        console.log(entry.name, entry.sick, radius);
        L.circle([entry.lat, entry.lng], {radius: radius, color: 'red', fillOpacity: 0.7})
            .addTo(mymap)
            .bindPopup("<b>" + entry.name + "</b>" +
                "<br />Infiziert: " + entry.sick +
                "<br />Geheilt: " + entry.cured +
                "<br />Todesfälle: " + entry.deaths
                );
    }
}

fetch('data.json')
    .then(res => res.json())
    .then(data => render(data));