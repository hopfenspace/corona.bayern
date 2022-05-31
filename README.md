# https://corona.bayern

Source code for a website displaying corona related statistics for bavaria (state of germany).

## Setting things setup
You need to get four javascript/css libraries and place them into web/assets
which are used by this code, but not included in the repository:

```bash
cd web/assets/
wget -O 'leaflet-1.3.4.css' 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.4/leaflet.css'
wget -O 'leaflet-1.3.4.js' 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.4/leaflet.js'
wget -O 'moment-2.29.3.js' 'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.3/moment.min.js'
wget -O 'chart-2.9.3.js' 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.bundle.min.js'
```

## Adapting to other states
This repository can easily be adapted to other germna states.
Simply obtain the OSM ID of your state and run the following overpass turbo query:

```overpass
area(3602145268);
rel
  [admin_level~"6"]
  (area);
out body;
>;
out skel qt;
```

Then export the result as GeoJSON. It is also a good idea to simplify this
GeoJSON (which can be pretty large) using a tool such as map mapshaper.org
