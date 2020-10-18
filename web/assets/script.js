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
    document.getElementById("deathSum").innerText = data.deathSum;
    document.getElementById("deathRate").innerText = Math.round(data.deathSum * 10000 / data.sickSum) / 100;
    var usePercent = document.location.search === "?percent";
    var useAbsolute = document.location.search === "?absolute";

    data.entries.sort((a, b) => b.sick - a.sick);

    for(var i = 0; i < data.entries.length; i++) {
        var entry = data.entries[i];
        var angle = entry.deaths / entry.sick * 360;
        var percent = Math.round(entry.sick * 10000 / entry.people) / 100;
        var deathRate = Math.round(entry.deaths * 10000 / entry.sick) / 100;

        if(entry.sick == 0)
        {
            var color = "#0180b2";
            var radius = Math.sqrt(3 * 3e5 / Math.PI);
        }
        else if(usePercent)
        {
            var color = "#6600cc";
            var radius = Math.sqrt(percent * 5e8 / Math.PI);
        }
        else if(useAbsolute)
        {
            var color = "red";
            var radius = Math.sqrt(entry.sick * 2e5 / Math.PI);
        }
        else // incidence
        {
            if(entry.incidence < 10)
                color = "green";
            else if(entry.incidence < 35)
                color = "grey";
            else if(entry.incidence < 50)
                color = "orange";
            else
                color = "red";

            radius = Math.sqrt(entry.incidence * 3e6 / Math.PI);
        }

        var text = "<b>" + entry.name + "</b>"
            + "<br />Inzidenzzahl: " + entry.incidence
            + "<br />Infiziert: " + entry.sick
            + "<br />Tote: " + entry.deaths
            + "<br />Durchseuchung: " + percent + "%"
            + "<br />Sterberate: " + deathRate + "%";
        L.semiCircle([entry.lat, entry.lng], {
                radius: radius,
                startAngle: angle,
                stopAngle: 360,
                color: color,
                fillOpacity: 0.7
            })
            .addTo(mymap)
            .bindTooltip(text, {sticky: true, direction: "top"});

        if(entry.deaths > 0)
        {
            text = "<b>" + entry.name + "</b>"
                + "<br />Tote: " + entry.deaths;
            L.semiCircle([entry.lat, entry.lng], {
                    radius: radius,
                    startAngle: 0,
                    stopAngle: angle,
                    color: 'black',
                    fillOpacity: 0.7
                })
                .addTo(mymap)
                .bindTooltip(text, {sticky: true, direction: "top"});
        }
    }
}

fetch('data.json', {cache: "no-cache"})
    .then(res => res.json())
    .then(data => render(data));