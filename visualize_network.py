"""
Global Airport & Flight Route Network Explorer
----------------------------------------------
Reads the OpenFlights data, builds the airport graph (airports = vertices,
routes = directed edges), computes the network measures, and writes ONE
self-contained dashboard page:  airport_map.html

Only the Python standard library is needed.

    python visualize_network.py

Then serve the folder and open the page:

    python -m http.server 8000
    http://localhost:8000/airport_map.html
"""

import csv
import json
import os
from collections import defaultdict

# ============================================================
# CONFIGURATION
# ============================================================
AIRPORT_FILE = "data/airports.dat"
ROUTE_FILE = "data/routes.dat"
TEMPLATE_FILE = "templates/dashboard.html"
OUTPUT_FILE = "airport_map.html"

REGIONS = [
    "Europe", "Asia", "Africa",
    "North America", "South America", "Oceania",
]

# ============================================================
# REGION DETECTION
# Country list first; time-zone prefix and a coarse lat/lon check
# are only fallbacks so that no airport ends up in an "Other" bucket.
# ============================================================
EUROPE = {
    "Albania", "Andorra", "Austria", "Belarus", "Belgium",
    "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus",
    "Czech Republic", "Czechia", "Denmark", "Estonia", "Finland",
    "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland",
    "Italy", "Kosovo", "Latvia", "Liechtenstein", "Lithuania",
    "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro",
    "Netherlands", "North Macedonia", "Macedonia", "Norway", "Poland",
    "Portugal", "Romania", "Russia", "San Marino", "Serbia",
    "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland",
    "Turkey", "Ukraine", "United Kingdom", "Vatican City",
    "Faroe Islands", "Greenland", "Guernsey", "Jersey", "Isle of Man",
    "Gibraltar",
}
ASIA = {
    "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh",
    "Bhutan", "Brunei", "Cambodia", "China", "Georgia", "India",
    "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan",
    "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon",
    "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal",
    "North Korea", "Oman", "Pakistan", "Palestine", "Philippines",
    "Qatar", "Saudi Arabia", "Singapore", "South Korea",
    "Sri Lanka", "Syria", "Taiwan", "Tajikistan", "Thailand",
    "Timor-Leste", "East Timor", "Turkmenistan",
    "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen",
    "Hong Kong", "Macau",
}
AFRICA = {
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso",
    "Burundi", "Cameroon", "Cape Verde", "Central African Republic",
    "Chad", "Comoros", "Congo (Brazzaville)", "Congo (Kinshasa)",
    "Congo", "Democratic Republic of the Congo",
    "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini",
    "Swaziland", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea",
    "Guinea-Bissau", "Ivory Coast", "Cote d'Ivoire", "Kenya",
    "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali",
    "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia",
    "Niger", "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal",
    "Seychelles", "Sierra Leone", "Somalia", "South Africa",
    "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia", "Uganda",
    "Zambia", "Zimbabwe", "Reunion", "Mayotte", "Western Sahara",
}
NORTH_AMERICA = {
    "Canada", "United States", "Mexico", "Guatemala", "Belize",
    "Honduras", "El Salvador", "Nicaragua", "Costa Rica", "Panama",
    "Cuba", "Jamaica", "Haiti", "Dominican Republic", "Bahamas",
    "Barbados", "Trinidad and Tobago", "Puerto Rico", "Bermuda",
    "Cayman Islands", "Aruba", "Netherlands Antilles", "Curacao",
    "Antigua and Barbuda", "Saint Lucia", "Grenada", "Dominica",
    "Saint Kitts and Nevis", "Saint Vincent and the Grenadines",
    "Virgin Islands", "British Virgin Islands", "Turks and Caicos Islands",
    "Anguilla", "Guadeloupe", "Martinique", "Montserrat",
    "Saint Pierre and Miquelon", "Sint Maarten", "Saint Martin",
    "Saint Barthelemy",
}
SOUTH_AMERICA = {
    "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
    "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela",
    "French Guiana", "Falkland Islands",
}
OCEANIA = {
    "Australia", "New Zealand", "Fiji", "Papua New Guinea", "Samoa",
    "Tonga", "Vanuatu", "Solomon Islands", "New Caledonia",
    "French Polynesia", "Guam", "Micronesia", "Palau",
    "Marshall Islands", "Kiribati", "Nauru", "Tuvalu", "Cook Islands",
    "Niue", "Norfolk Island", "Northern Mariana Islands",
    "American Samoa", "Wallis and Futuna", "Christmas Island",
    "Cocos (Keeling) Islands",
}
COUNTRY_TO_REGION = {}
for _name, _set in (
    ("Europe", EUROPE), ("Asia", ASIA), ("Africa", AFRICA),
    ("North America", NORTH_AMERICA), ("South America", SOUTH_AMERICA),
    ("Oceania", OCEANIA),
):
    for _c in _set:
        COUNTRY_TO_REGION[_c] = _name


def get_region(country, tz, lat, lon):
    """Return one of REGIONS for an airport."""
    if country in COUNTRY_TO_REGION:
        return COUNTRY_TO_REGION[country]

    prefix = tz.split("/")[0] if tz and tz != "\\N" else ""
    if prefix == "Europe":
        return "Europe"
    if prefix == "Asia":
        return "Asia"
    if prefix == "Africa":
        return "Africa"
    if prefix in ("Australia", "Pacific"):
        return "Oceania"
    if prefix == "America":
        return "South America" if lat < 8 and lon < -34 else "North America"

    # Last resort: coarse bounding boxes
    if lon < -30:
        return "South America" if lat < 8 and lon > -85 else "North America"
    if lon > 110 and lat < 0:
        return "Oceania"
    if -20 <= lon <= 55 and lat < 35:
        return "Africa"
    if -25 <= lon <= 45 and lat >= 35:
        return "Europe"
    return "Asia"


# ============================================================
# LOAD DATA
# ============================================================
def read_csv(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        yield from csv.reader(f)


def load_airports(path):
    """IATA code -> airport dict (airports without an IATA code are skipped;
    keyed by IATA so the counts match analyze_graph.py)."""
    airports = {}
    for row in read_csv(path):
        if len(row) < 12:
            continue
        iata = row[4].strip()
        if not iata or iata == "\\N":
            continue
        try:
            lat, lon = float(row[6]), float(row[7])
        except ValueError:
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        country = row[3].strip()
        if iata in airports:          # keep the first record per IATA code
            continue
        airports[iata] = {
            "iata": iata,
            "name": row[1].strip(),
            "city": row[2].strip(),
            "country": country,
            "lat": round(lat, 3),
            "lon": round(lon, 3),
            "region": get_region(country, row[11].strip(), lat, lon),
        }
    return airports


def load_edges(path, airports):
    """Unique directed edges (source IATA, destination IATA)."""
    edges = set()
    for row in read_csv(path):
        if len(row) < 6:
            continue
        s, d = row[2].strip(), row[4].strip()
        if s in airports and d in airports:
            edges.add((s, d))
    return edges


# ============================================================
# GRAPH MEASURES
# ============================================================
def giant_component_size(nodes, neighbours):
    seen, best = set(), 0
    for start in nodes:
        if start in seen:
            continue
        stack, size = [start], 0
        seen.add(start)
        while stack:
            u = stack.pop()
            size += 1
            for v in neighbours[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        best = max(best, size)
    return best


def main():
    print("=" * 56)
    print("GLOBAL AIRPORT & FLIGHT ROUTE NETWORK EXPLORER")
    print("=" * 56)

    airports = load_airports(AIRPORT_FILE)
    edges = load_edges(ROUTE_FILE, airports)
    print(f"Airports with IATA code : {len(airports)}")
    print(f"Unique directed routes  : {len(edges)}")

    out_nb, in_nb, nb = defaultdict(set), defaultdict(set), defaultdict(set)
    for s, d in edges:
        if s == d:                    # self-loops count as routes, not links
            continue
        out_nb[s].add(d)
        in_nb[d].add(s)
        nb[s].add(d)
        nb[d].add(s)

    # Keep airports that have at least one route (isolated ones are noise).
    connected = sorted(nb, key=lambda a: (-len(nb[a]), airports[a]["iata"]))
    index = {aid: i for i, aid in enumerate(connected)}

    giant = giant_component_size(connected, nb)
    print(f"Connected airports      : {len(connected)}")
    print(f"Largest component       : {giant} "
          f"({giant / len(connected):.1%})")

    # ---- compact payload for the page -------------------------
    # airport row: [iata, name, city, country, lat, lon, regionIdx,
    #               connections, outbound, inbound]
    rows = []
    for aid in connected:
        a = airports[aid]
        rows.append([
            a["iata"], a["name"], a["city"], a["country"],
            a["lat"], a["lon"], REGIONS.index(a["region"]),
            len(nb[aid]), len(out_nb[aid]), len(in_nb[aid]),
        ])

    # Undirected unique pairs [i, j, twoWay] keep the page light:
    # twoWay = 1 when the route exists in both directions.
    pairs = {}
    for s, d in edges:
        if s == d:
            continue
        i, j = index[s], index[d]
        key = (i, j) if i < j else (j, i)
        pairs[key] = pairs.get(key, 0) | (1 if i < j else 2)
    pair_rows = [[i, j, 1 if m == 3 else 0] for (i, j), m in pairs.items()]

    region_counts = [0] * len(REGIONS)
    for r in rows:
        region_counts[r[6]] += 1

    # ---- extra facts for the "About this graph" panel ----------
    n_all = len(airports)
    pendant = sum(1 for a in connected if len(nb[a]) == 1)
    edges_no_loop = [(s, d) for s, d in edges if s != d]
    flow = [[0] * len(REGIONS) for _ in REGIONS]
    for s, d in edges_no_loop:
        flow[REGIONS.index(airports[s]["region"])][
            REGIONS.index(airports[d]["region"])] += 1
    bucket_edges = [(1, 1), (2, 4), (5, 9), (10, 24), (25, 49),
                    (50, 99), (100, 10**9)]
    buckets = [
        sum(1 for a in connected if lo <= len(nb[a]) <= hi)
        for lo, hi in bucket_edges
    ]

    payload = {
        "regions": REGIONS,
        "regionCounts": region_counts,
        "airports": rows,
        "pairs": pair_rows,
        "stats": {
            "airports": len(connected),
            "routes": len(edges),
            "giantPct": round(100 * giant / len(connected), 1),
            "giantSize": giant,
            "allAirports": n_all,
            "isolated": n_all - len(connected),
            "pendant": pendant,
            "density": len(edges) / (n_all * (n_all - 1)),
            "avgConn": round(sum(len(nb[a]) for a in connected)
                             / len(connected), 1),
            "maxConn": len(nb[connected[0]]),
        },
        "degreeBuckets": {
            "labels": ["1", "2–4", "5–9", "10–24", "25–49", "50–99", "100+"],
            "counts": buckets,
        },
        "flow": flow,
    }

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    data_json = json.dumps(payload, separators=(",", ":"),
                           ensure_ascii=False).replace("</", "<\\/")
    page = template.replace("/*__DATA__*/null", data_json)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(page)

    print()
    print("Top 5 hubs (distinct connected airports):")
    for aid in connected[:5]:
        a = airports[aid]
        print(f"  {a['iata']:<4} {a['name']:<42} {len(nb[aid])}")
    print(f"\nSaved {OUTPUT_FILE}  ({os.path.getsize(OUTPUT_FILE) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
