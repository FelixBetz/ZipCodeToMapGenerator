"""This module parses a input CSV list and generate some maps"""
import csv
import os

import folium
from folium.plugins import MarkerCluster
from folium import plugins

import pgeocode

# generate output directory
OUTPUT_DIR_PATH = './output/'
if not os.path.exists(OUTPUT_DIR_PATH):
    os.makedirs(OUTPUT_DIR_PATH)

# parse PLZs from csv file
# format: delimiter: ';'
#line   | zipcode;locationName
# -------------------------------------
#   0   | 88471;Baustetten
#   1   | 89134;Blaustein
#   ... |    ........
ZIP_CODE_FILE_NAME = 'input_zipcodes.csv'

zip_codes = []
with open(ZIP_CODE_FILE_NAME, newline='',encoding='utf-8') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
    for i, row in enumerate(spamreader):
        if i == 0:
            pass
        else:
            zip_codes.append((row[0], row[1]))

# Get longitude and latitude for each zipcode
nomi = pgeocode.Nominatim('de')
markerLocs = []
for zip_code in zip_codes:
    zip_code_coords = nomi.query_postal_code(zip_code[0])
    markerLocs.append(
        [zip_code_coords['latitude'], zip_code_coords['longitude']])

# calculate 'middle_point'
lat_min = min(markerLocs, key=lambda loc: float(loc[0]))[0]
lat_max = max(markerLocs, key=lambda loc: float(loc[0]))[0]

long_min = min(markerLocs, key=lambda loc: float(loc[1]))[1]
long_max = max(markerLocs, key=lambda loc: float(loc[1]))[1]

loc_long = (long_max + long_min) / 2
loc_lat = (lat_max + lat_min) / 2

###########################################################################################
# genearte makers map
mapObj = folium.Map([loc_lat, loc_long],
                    zoom_start=7, tiles="Stamen Toner")
mCluster = MarkerCluster(name='Zeltlager Teilnehmer').add_to(mapObj)

# create markers form PLZ coordinates array
for i, pnt in enumerate(markerLocs):
    zipcode =  zip_codes[i][0]
    location = zip_codes[i][1]
    x = pnt[0]
    y = pnt[1]
    folium.Marker(
        location=[pnt[0], pnt[1]],
        popup=f"{zipcode} {location}\r\n({x}°| {y}°)"
    ).add_to(mCluster)

minimap = plugins.MiniMap()
mapObj.add_child(minimap)
FORMATTER = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
plugins.MousePosition(
    position='topright',
    separator=' | ',
    empty_string='NaN',
    lng_first=True,
    num_digits=20,
    prefix='Coordinates:',
    lat_formatter=FORMATTER,
    lng_formatter=FORMATTER,
).add_to(mapObj)


m = folium.LayerControl().add_to(mapObj)
# save the map object as html
mapObj.save(OUTPUT_DIR_PATH+'markermap.html')

###########################################################################################
# genearte heatmap
heatmap = folium.Map([loc_lat, loc_long],
                     zoom_start=7, tiles="Stamen Toner")  # tiles="Stamen Toner"
plugins.HeatMap(markerLocs).add_to(heatmap)
heatmap.save(OUTPUT_DIR_PATH+'heatmap.html')
