import csv

import os

import html

from collections import Counter



import folium

from folium import FeatureGroup, LayerControl

from folium.plugins import Fullscreen





# ============================================================

# CONFIGURATION

# ============================================================



AIRPORT_FILE = "data/airports.dat"

ROUTE_FILE = "data/routes.dat"



OUTPUT_FILE = "airport_map.html"



# Number of important airports to display

TOP_AIRPORTS = 50



# Maximum number of routes to display

MAX_ROUTES = 500



# Map starting position

START_LOCATION = [20, 0]

START_ZOOM = 2





# ============================================================

# REGION COLORS

# ============================================================



REGION_COLORS = {

    "Europe": "red",

    "Asia": "blue",

    "Africa": "green",

    "North America": "purple",

    "South America": "orange",

    "Oceania": "darkred",

    "Other": "gray",

}





# ============================================================

# REGION DETECTION

# ============================================================



def get_region(country):

    """

    Approximate geographic region based on country name.

    """



    europe = {

        "Albania", "Andorra", "Austria", "Belarus", "Belgium",

        "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus",

        "Czech Republic", "Czechia", "Denmark", "Estonia", "Finland",

        "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland",

        "Italy", "Kosovo", "Latvia", "Liechtenstein", "Lithuania",

        "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro",

        "Netherlands", "North Macedonia", "Norway", "Poland",

        "Portugal", "Romania", "Russia", "San Marino", "Serbia",

        "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland",

        "Turkey", "Ukraine", "United Kingdom", "Vatican City"

    }



    asia = {

        "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh",

        "Bhutan", "Brunei", "Cambodia", "China", "Georgia", "India",

        "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan",

        "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon",

        "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal",

        "North Korea", "Oman", "Pakistan", "Palestine", "Philippines",

        "Qatar", "Saudi Arabia", "Singapore", "South Korea",

        "Sri Lanka", "Syria", "Taiwan", "Tajikistan", "Thailand",

        "Timor-Leste", "Turkmenistan", "United Arab Emirates",

        "Uzbekistan", "Vietnam", "Yemen"

    }



    africa = {

        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso",

        "Burundi", "Cameroon", "Cape Verde", "Central African Republic",

        "Chad", "Comoros", "Congo", "Democratic Republic of the Congo",

        "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini",

        "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea",

        "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia",

        "Libya", "Madagascar", "Malawi", "Mali", "Mauritania",

        "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger",

        "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal",

        "Seychelles", "Sierra Leone", "Somalia", "South Africa",

        "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia",

        "Uganda", "Zambia", "Zimbabwe"

    }



    north_america = {

        "Canada", "United States", "Mexico", "Guatemala", "Belize",

        "Honduras", "El Salvador", "Nicaragua", "Costa Rica", "Panama",

        "Cuba", "Jamaica", "Haiti", "Dominican Republic",

        "Bahamas", "Barbados", "Trinidad and Tobago"

    }



    south_america = {

        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia",

        "Ecuador", "Guyana", "Paraguay", "Peru", "Suriname",

        "Uruguay", "Venezuela", "French Guiana"

    }



    oceania = {

        "Australia", "New Zealand", "Fiji", "Papua New Guinea",

        "Samoa", "Tonga", "Vanuatu", "Solomon Islands",

        "New Caledonia", "French Polynesia", "Guam",

        "Micronesia", "Palau", "Marshall Islands"

    }



    if country in europe:

        return "Europe"



    if country in asia:

        return "Asia"



    if country in africa:

        return "Africa"



    if country in north_america:

        return "North America"



    if country in south_america:

        return "South America"



    if country in oceania:

        return "Oceania"



    return "Other"





# ============================================================

# LOAD AIRPORT DATA

# ============================================================



def load_airports(filename):



    airports = {}



    if not os.path.exists(filename):

        raise FileNotFoundError(

            f"Airport file not found: {filename}"

        )



    with open(

        filename,

        "r",

        encoding="utf-8",

        errors="replace"

    ) as file:



        reader = csv.reader(

            file,

            delimiter=",",

            quotechar='"'

        )



        for row in reader:



            if len(row) < 8:

                continue



            try:

                airport_id = row[0].strip()



                name = row[1].strip()

                city = row[2].strip()

                country = row[3].strip()



                iata = row[4].strip()

                icao = row[5].strip()



                latitude = float(row[6])

                longitude = float(row[7])



                # Ignore invalid coordinates

                if not (-90 <= latitude <= 90):

                    continue



                if not (-180 <= longitude <= 180):

                    continue



                # Some OpenFlights records have \N

                if iata == "\\N":

                    iata = ""



                if icao == "\\N":

                    icao = ""



                airports[airport_id] = {

                    "id": airport_id,

                    "name": name,

                    "city": city,

                    "country": country,

                    "iata": iata,

                    "icao": icao,

                    "lat": latitude,

                    "lon": longitude,

                    "region": get_region(country),

                }



            except (ValueError, IndexError):

                continue



    return airports





# ============================================================

# LOAD ROUTE DATA

# ============================================================



def load_routes(filename):



    routes = []



    if not os.path.exists(filename):

        raise FileNotFoundError(

            f"Route file not found: {filename}"

        )



    with open(

        filename,

        "r",

        encoding="utf-8",

        errors="replace"

    ) as file:



        reader = csv.reader(

            file,

            delimiter=",",

            quotechar='"'

        )



        for row in reader:



            if len(row) < 6:

                continue



            airline = row[0].strip()



            source_airport = row[2].strip()

            source_id = row[3].strip()



            destination_airport = row[4].strip()

            destination_id = row[5].strip()



            # Ignore invalid route IDs

            if source_id == "\\N" or destination_id == "\\N":

                continue



            routes.append({

                "airline": airline,

                "source": source_id,

                "destination": destination_id,

                "source_code": source_airport,

                "destination_code": destination_airport,

            })



    return routes





# ============================================================

# MAIN

# ============================================================



print()

print("=" * 60)

print("GLOBAL AIRPORT & FLIGHT ROUTE NETWORK")

print("=" * 60)





# ------------------------------------------------------------

# Load data

# ------------------------------------------------------------



print("\nLoading airport data...")



airports = load_airports(AIRPORT_FILE)



print(f"Airports loaded: {len(airports)}")





print("\nLoading route data...")



all_routes = load_routes(ROUTE_FILE)



print(f"Routes loaded: {len(all_routes)}")





# ============================================================

# REMOVE ROUTES WITH MISSING AIRPORTS

# ============================================================



valid_routes = []



for route in all_routes:



    source = route["source"]

    destination = route["destination"]



    if source in airports and destination in airports:



        valid_routes.append(route)





print(f"Valid routes: {len(valid_routes)}")





# ============================================================

# CALCULATE AIRPORT CONNECTIONS

# ============================================================



connections = Counter()



out_degree = Counter()

in_degree = Counter()



for route in valid_routes:



    source = route["source"]

    destination = route["destination"]



    connections[source] += 1

    connections[destination] += 1



    out_degree[source] += 1

    in_degree[destination] += 1





# ============================================================

# SELECT TOP AIRPORTS

# ============================================================



top_airports = [

    airport_id

    for airport_id, count

    in connections.most_common(TOP_AIRPORTS)

]





selected_set = set(top_airports)





print()

print("=" * 60)

print(f"TOP {TOP_AIRPORTS} CONNECTED AIRPORTS")

print("=" * 60)



for rank, airport_id in enumerate(top_airports[:10], 1):



    airport = airports[airport_id]



    print(

        f"{rank:2}. "

        f"{airport['iata']:<4} "

        f"{airport['name']:<45} "

        f"{connections[airport_id]}"

    )





# ============================================================

# SELECT ROUTES BETWEEN TOP AIRPORTS

# ============================================================



display_routes = []



for route in valid_routes:



    source = route["source"]

    destination = route["destination"]



    if source in selected_set and destination in selected_set:



        display_routes.append(route)





# ------------------------------------------------------------

# Sort routes so the most connected relationships appear first

# ------------------------------------------------------------



display_routes.sort(

    key=lambda r: (

        connections[r["source"]] +

        connections[r["destination"]]

    ),

    reverse=True

)





# Limit routes

display_routes = display_routes[:MAX_ROUTES]





print()

print("=" * 60)

print("VISUALIZATION DATA")

print("=" * 60)



print(f"Selected airports : {len(top_airports)}")

print(f"Displayed routes  : {len(display_routes)}")





# ============================================================

# CREATE MAP

# ============================================================



m = folium.Map(

    location=START_LOCATION,

    zoom_start=START_ZOOM,

    tiles=None,

    control_scale=True,

    prefer_canvas=True

)





# ============================================================

# BASE MAPS

# ============================================================



# OpenStreetMap

folium.TileLayer(

    tiles="OpenStreetMap",

    name="World Street Map",

    control=True,

    show=False

).add_to(m)





# Esri Satellite

folium.TileLayer(

    tiles=(

        "https://server.arcgisonline.com/"

        "ArcGIS/rest/services/World_Imagery/"

        "MapServer/tile/{z}/{y}/{x}"

    ),

    attr="Tiles © Esri",

    name="Satellite",

    control=True,

    show=True

).add_to(m)





# ============================================================

# FLIGHT ROUTE FEATURE GROUP

# ============================================================



route_layer = FeatureGroup(

    name="✈ Flight Routes",

    show=True,

    overlay=True

)



route_layer.add_to(m)





# ============================================================
# AIRPORT FEATURE GROUPS — FILTER BY REGION
# ============================================================

airport_layers = {}

for region in REGION_COLORS:
    airport_layers[region] = FeatureGroup(
        name=f"Airports — {region}",
        show=True,
        overlay=True
    )
    airport_layers[region].add_to(m)





# ============================================================

# ADD FLIGHT ROUTES

# ============================================================



for route in display_routes:



    source = airports[route["source"]]

    destination = airports[route["destination"]]



    source_code = (

        source["iata"]

        if source["iata"]

        else source["icao"]

    )



    destination_code = (

        destination["iata"]

        if destination["iata"]

        else destination["icao"]

    )



    popup_text = f"""

    <div style="width:220px;">

        <h4>✈ Flight Route</h4>



        <b>{html.escape(source_code)}</b>

        →

        <b>{html.escape(destination_code)}</b>



        <br><br>



        {html.escape(source["city"])},

        {html.escape(source["country"])}



        <br>

        ↓

        <br>



        {html.escape(destination["city"])},

        {html.escape(destination["country"])}



        <br><br>



        Airline:

        <b>{html.escape(route["airline"])}</b>

    </div>

    """



    folium.PolyLine(

        locations=[

            [source["lat"], source["lon"]],

            [destination["lat"], destination["lon"]]

        ],

        color="blue",

        weight=1.5,

        opacity=0.45,

        popup=folium.Popup(

            popup_text,

            max_width=300

        ),

        tooltip=(

            f"{source_code} → {destination_code}"

        )

    ).add_to(route_layer)





# ============================================================

# ADD AIRPORT MARKERS

# ============================================================



for airport_id in top_airports:



    airport = airports[airport_id]



    region = airport["region"]



    color = REGION_COLORS.get(

        region,

        "gray"

    )



    code = (

        airport["iata"]

        if airport["iata"]

        else airport["icao"]

    )



    airport_popup = f"""

    <div style="width:260px;">



        <h3 style="margin-bottom:8px;">

            ✈ {html.escape(code)}

        </h3>



        <b>{html.escape(airport["name"])}</b>



        <br><br>



        <b>City:</b>

        {html.escape(airport["city"])}



        <br>



        <b>Country:</b>

        {html.escape(airport["country"])}



        <br>



        <b>Region:</b>

        {html.escape(region)}



        <br><br>



        <b>Total Connections:</b>

        {connections[airport_id]}



        <br>



        <b>Outgoing:</b>

        {out_degree[airport_id]}



        <br>



        <b>Incoming:</b>

        {in_degree[airport_id]}



    </div>

    """



    folium.CircleMarker(

        location=[

            airport["lat"],

            airport["lon"]

        ],

        radius=7,

        color="black",

        weight=1,

        fill=True,

        fill_color=color,

        fill_opacity=0.9,

        popup=folium.Popup(

            airport_popup,

            max_width=350

        ),

        tooltip=(

            f"{code} — "

            f"{airport['name']} "

            f"({connections[airport_id]} connections)"

        )

    ).add_to(airport_layers[region])





# ============================================================

# TITLE PANEL

# ============================================================



title_html = """

<div style="

    position: fixed;

    top: 15px;

    left: 60px;

    z-index: 9999;

    background: white;

    padding: 15px 25px;

    border-radius: 12px;

    box-shadow: 0 3px 12px rgba(0,0,0,0.25);

">



    <div style="

        font-size: 25px;

        font-weight: bold;

        color: #222;

    ">

        🌎 Global Airport & Flight Route Network

    </div>



    <div style="

        font-size: 15px;

        color: #555;

        margin-top: 5px;

    ">

        Interactive Graph Visualization

    </div>



</div>

"""



m.get_root().html.add_child(

    folium.Element(title_html)

)





# ============================================================

# NETWORK STATISTICS PANEL

# ============================================================



statistics_html = f"""

<div style="

    position: fixed;

    bottom: 25px;

    left: 20px;

    z-index: 9999;



    background: white;



    padding: 18px;



    border-radius: 12px;



    box-shadow:

        0 3px 12px rgba(0,0,0,0.25);



    width: 270px;



    font-family: Arial;

">



    <div style="

        font-size: 18px;

        font-weight: bold;

        margin-bottom: 12px;

    ">

        📊 Network Statistics

    </div>



    <b>Selected Airports:</b>

    {len(top_airports)}



    <br>



    <b>Displayed Routes:</b>

    {len(display_routes)}



    <br>



    <b>Dataset Airports:</b>

    {len(airports)}



    <br>



    <b>Dataset Routes:</b>

    {len(valid_routes)}



    <br><br>



    <b>Network Coverage:</b>

    Top {TOP_AIRPORTS} airports



</div>

"""



m.get_root().html.add_child(

    folium.Element(statistics_html)

)





# ============================================================

# TOP CONNECTED AIRPORTS PANEL

# ============================================================



top_rows = ""



for rank, airport_id in enumerate(

    top_airports[:10],

    1

):



    airport = airports[airport_id]



    code = (

        airport["iata"]

        if airport["iata"]

        else airport["icao"]

    )



    top_rows += f"""

    <tr>

        <td style="padding:4px 8px;">

            {rank}

        </td>



        <td style="padding:4px 8px;">

            <b>{html.escape(code)}</b>

        </td>



        <td style="padding:4px 8px;">

            {connections[airport_id]}

        </td>

    </tr>

    """





top_airports_html = f"""

<div style="

    position: fixed;

    top: 175px;

    right: 20px;

    z-index: 9999;



    background: white;



    padding: 15px;



    border-radius: 12px;



    box-shadow:

        0 3px 12px rgba(0,0,0,0.25);



    width: 260px;



    font-family: Arial;

">



    <div style="

        font-size: 18px;

        font-weight: bold;

        margin-bottom: 10px;

    ">

        🏆 Top Connected Airports

    </div>



    <table style="

        width:100%;

        border-collapse:collapse;

        font-size:14px;

    ">



        <tr style="

            border-bottom:1px solid #ddd;

        ">



            <th style="text-align:left;">

                #

            </th>



            <th style="text-align:left;">

                Airport

            </th>



            <th style="text-align:left;">

                Connections

            </th>



        </tr>



        {top_rows}



    </table>



</div>

"""



m.get_root().html.add_child(

    folium.Element(top_airports_html)

)





# ============================================================

# REGION LEGEND

# ============================================================



legend_rows = ""



for region, color in REGION_COLORS.items():



    legend_rows += f"""

    <div style="margin:5px 0;">



        <span style="

            display:inline-block;

            width:12px;

            height:12px;



            background:{color};



            border-radius:50%;



            margin-right:8px;

        "></span>



        {region}



    </div>

    """





legend_html = f"""

<div style="

    position: fixed;

    bottom: 30px;

    right: 20px;

    z-index: 9999;



    background:white;



    padding:15px;



    border-radius:12px;



    box-shadow:

        0 3px 12px rgba(0,0,0,0.25);



    font-family:Arial;



    font-size:14px;

">



    <div style="

        font-size:17px;

        font-weight:bold;

        margin-bottom:8px;

    ">

        🌎 Airport Regions

    </div>



    {legend_rows}



</div>

"""



m.get_root().html.add_child(

    folium.Element(legend_html)

)





# ============================================================

# AIRPORT SEARCH

# ============================================================



search_data = []



for airport_id in top_airports:



    airport = airports[airport_id]



    code = (

        airport["iata"]

        if airport["iata"]

        else airport["icao"]

    )



    search_data.append({

        "code": code,

        "name": airport["name"],

        "city": airport["city"],

        "country": airport["country"],

        "lat": airport["lat"],

        "lon": airport["lon"]

    })





import json



search_json = json.dumps(

    search_data

)





search_html = f"""

<div style="

    position: fixed;

    top: 75px;

    left: 15px;

    z-index: 9999;

">



    <input

        id="airportSearch"

        type="text"

        placeholder="Search airport..."

        style="

            width:190px;

            padding:9px;



            border:1px solid #aaa;

            border-radius:7px;



            font-size:14px;

            box-shadow:0 2px 6px rgba(0,0,0,0.2);

        "

    >



    <div

        id="searchResults"

        style="

            display:none;



            background:white;



            width:210px;



            max-height:250px;



            overflow-y:auto;



            border-radius:7px;



            box-shadow:

                0 3px 10px rgba(0,0,0,0.25);



            margin-top:4px;

        "

    ></div>



</div>



<script>



var airportSearchData = {search_json};



var searchBox =

    document.getElementById("airportSearch");



var results =

    document.getElementById("searchResults");





searchBox.addEventListener(

    "input",

    function() {{



        var query =

            searchBox.value

                .toLowerCase()

                .trim();



        results.innerHTML = "";



        if (query.length === 0) {{



            results.style.display = "none";



            return;

        }}



        var matches =

            airportSearchData.filter(

                function(a) {{



                    return (

                        a.code.toLowerCase().includes(query) ||

                        a.name.toLowerCase().includes(query) ||

                        a.city.toLowerCase().includes(query) ||

                        a.country.toLowerCase().includes(query)

                    );



                }}

            ).slice(0, 8);





        if (matches.length === 0) {{



            results.innerHTML =

                "<div style='padding:10px;'>No airport found</div>";



            results.style.display = "block";



            return;

        }}





        matches.forEach(

            function(a) {{



                var item =

                    document.createElement("div");



                item.style.padding = "9px";



                item.style.cursor = "pointer";



                item.style.borderBottom =

                    "1px solid #eee";



                item.innerHTML =

                    "<b>" +

                    a.code +

                    "</b> — " +

                    a.city +

                    "<br>" +

                    "<small>" +

                    a.country +

                    "</small>";





                item.onclick =

                    function() {{



                        map.setView(

                            [a.lat, a.lon],

                            6

                        );



                        searchBox.value =

                            a.code;



                        results.style.display =

                            "none";



                    }};





                results.appendChild(item);



            }}

        );





        results.style.display =

            "block";



    }}

);



</script>

"""



m.get_root().html.add_child(

    folium.Element(search_html)

)





# ============================================================

# FULLSCREEN BUTTON

# ============================================================



Fullscreen(

    position="topleft",

    title="Full Screen",

    title_cancel="Exit Full Screen",

    force_separate_button=True

).add_to(m)





# ============================================================

# LAYER CONTROL

# ============================================================



LayerControl(

    position="topright",

    collapsed=False

).add_to(m)





# ============================================================

# SAVE MAP

# ============================================================



m.save(OUTPUT_FILE)





# ============================================================

# FINAL OUTPUT

# ============================================================



print()

print("=" * 60)

print("WORLD MAP CREATED SUCCESSFULLY!")

print("=" * 60)



print(f"Airports selected : {len(top_airports)}")

print(f"Routes displayed  : {len(display_routes)}")

print(f"Dataset airports  : {len(airports)}")

print(f"Dataset routes     : {len(valid_routes)}")



print()

print(f"Open {OUTPUT_FILE} in your browser.")

print()
