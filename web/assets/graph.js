var labels = [];
var infected = [];
var deaths = [];

var params = {};
document.location.search.slice(1).split("&").forEach(entry => {
    var split = entry.split("=");
    params[split[0]] = decodeURIComponent(split[1]);
});
var start = parseInt(params.start) || Date.now() - 14 * 24 * 60 * 60 * 1000;
var end = parseInt(params.end) || Date.now();
var linear = params.linear === "true";

var startEl = document.getElementById("startDate");
var endEl = document.getElementById("endDate");

startEl.valueAsNumber = start;
endEl.valueAsNumber = end;

function loadNewRange()
{
    document.location.replace(`?linear=${linear}&start=${startEl.valueAsNumber}&end=${endEl.valueAsNumber}`);
}

function padString(s, len, pad)
{
    s = String(s);
    while(s.length < len)
        s = pad + s;

    return s;
}

async function loadData(date)
{
    var year = padString(date.getFullYear(), 4, '0');
    var month = padString(date.getMonth() + 1, 2, '0');
    var day = padString(date.getDate(), 2, '0');
    var res = await fetch(`history/${year}-${month}-${day}T00:00:00.json`);
    var json = await res.json();

    return {
        label: `${year}-${month}-${day}`,
        infected: json.sickSum,
        deaths: json.deathSum,
    };
}

async function loadAllDays(start, end)
{
    end = end.getTime();
    var curr = start.getTime();
    var promises = [];
    while(curr < end)
    {
        var load = loadData(new Date(curr))
            .catch(err => null);
        promises.push(load);

        curr += 24 * 60 * 60 * 1000;
    }

    var data = await Promise.all(promises);
    console.log(data);
    for(var entry of data)
    {
        if (!entry)
            continue;
        
        labels.push(entry.label);
        infected.push(entry.infected);
        deaths.push(entry.deaths);
    }
    chart.update();
}

var canvas = document.getElementsByTagName('canvas')[0];
var chart = new Chart(canvas, {
    type: 'line',
    data: {
        labels,
        datasets: [
            {
                label: 'Infiziert',
                borderColor: 'red',
                fill: false,
                data: infected,
            },
            {
                label: 'Tote',
                borderColor: 'black',
                fill: false,
                data: deaths,
            },
        ],
    },
    options: {
        //responsive: true,
        //maintainAspectRatio: false,
        scales: {
            xAxes: [{
                type: 'time',
                time: {
                    parser: 'YYYY-MM-DD',
                    tooltipFormat: 'YYYY-MM-DD'
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Date'
                },
            }],
            yAxes: [{
                type: linear ? 'linear' : 'logarithmic',
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
});

loadAllDays(new Date(start), new Date(end))
    .then(() => console.log('finished loading all days', labels, infected, deaths));
