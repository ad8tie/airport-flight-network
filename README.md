# Interactive Visualization of Global Airport and Flight Route Networks

An interactive graph-visualization project that explores global airport connectivity using airport locations and flight-route data. The application displays airports on a geographic map, overlays directed flight routes, and provides search, region filters, network statistics, and a ranking of highly connected airports.

## Features

- Clean dark dashboard: one search bar, a small filter panel, the map, and a single side panel.
- Airports drawn at their real coordinates; dot **colour = region**, dot **size = number of directly connected airports**.
- Overview shows only routes between the 60 busiest hubs (curved arcs), so the map stays readable.
- **Select any airport** (click a dot, use search, or click a hub) to see all of its routes, its in/out connections, rank, and busiest links.
- Search by airport code, name, city or country (press `/` to focus, arrow keys + Enter to pick, `Esc` to clear).
- Filters: region toggles, minimum-connections slider, routes on/off, Dark / Satellite / Streets map style.
- Top-10 hubs ranking that follows the region filter, linked to the map by hover (brushing and linking).
- "About this graph" panel: vertices, edges, density, isolated/pendant counts, degree distribution, region route matrix.
- Deep links: opening `airport_map.html#JFK` selects that airport.
- Graph analysis script reporting degree measures, density, connected components and isolated airports (CSV/text exports).

## Project goal and key questions

The app lets a user explore the world's airline network and answer:

1. Which airports are the biggest hubs, and how do they compare?
2. How are airports and routes spread across world regions?
3. Is the network one connected whole? How many airports are isolated or have only one neighbour?
4. Where can I fly directly from a given airport, and how far does its reach extend?

## Graph model (formal description)

- **Vertices:** 6,072 airports with an IATA code (a finite set).
- **Edges:** 37,042 unique directed routes (source -> destination); duplicate airline records for the same ordered pair count once.
- **Degree:** in-degree and out-degree per airport; the app's "connections" = number of distinct neighbouring airports.
- **Isolated vertices:** 2,815 airports have no route in the dataset (the map plots the 3,257 that do).
- **Pendant vertices:** 747 airports have exactly one neighbour.
- **Density:** 0.00100 (a sparse graph).
- **Connectivity:** one giant weakly connected component of 3,231 airports (99.2% of airports with routes).
- Run `python analyze_graph.py` for the full report; the in-app **About this graph** button shows the same facts, the degree distribution, and a region-to-region route matrix.

## Visualization pipeline (reference model)

```text
Raw data            Data tables              Visual structures          Views / interaction
data/airports.dat   cleaned airport table    dots (airports)            map (zoom/pan, 3 basemaps)
data/routes.dat  -> route edge list       -> arcs (routes)           -> hub list <-> map (linked)
                    graph + degree,          bars (hubs, degrees)       region filter, min-degree slider,
                    region, components       matrix (region flows)      search, details panel, about panel
```

1. **Raw data -> tables:** `visualize_network.py` loads both files, drops airports without IATA code or valid coordinates, removes routes with unknown airports, assigns a region to every airport.
2. **Tables -> visual structures:** degrees, regions and region-to-region counts are computed and embedded in the page as compact JSON.
3. **Structures -> views:** `templates/dashboard.html` draws the map, hub list, details panel and about panel, and wires up the interaction.

### Visual mapping

| Data attribute | Type | Visual variable | Why it suits the data |
|---|---|---|---|
| Latitude / longitude | spatial | Position on map | Airports have a real location; geography is the natural layout |
| Region | categorical | Colour (6 hues) | Hue distinguishes categories without implying order |
| Number of connections | quantitative | Dot size (and bar length in hub list) | Size/length order quantities well; big = important hub |
| Route (edge) | relation | Curved line between two dots | Lines express connection; curvature separates overlapping routes |
| Selected airport | focus | Amber ring and amber routes | A single contrasting accent draws attention |
| Route counts between regions | quantitative | Cell darkness in matrix | Intensity shows aggregate volume |

Shape is not used: a single marker shape keeps the map simple, and the data has no second categorical attribute that needs it.

## Interaction techniques

- **Zoom / pan** the map.
- **Search** by code, name, city or country (`/` focuses the box).
- **Filtering:** region toggles and a minimum-connections slider.
- **Details on demand:** click a dot, hub or link chip to see that airport's routes, in/out counts, rank and busiest links.
- **Brushing and linking:** hovering a hub in the list rings it on the map, and hovering a dot on the map highlights its row in the list. Region filters update the map and the hub ranking together.
- **Overview first:** the map starts with hub-to-hub routes only; full routes appear on selection.
- **About this graph:** formal graph facts, degree distribution and region route matrix on demand.

## Gestalt principles and overload

- **Similarity:** same colour = same region; same shape = same kind of thing (airport).
- **Proximity:** nearby airports sit close on the map and read as clusters (Europe, East Asia, US).
- **Connectedness:** a line joins two airports, so a route reads as a link and the amber routes of a selected airport read as one object.
- **Continuity:** smooth arcs let the eye follow a route across the map.
- **Closure:** a hub with its fan of routes is perceived as one unit (a star shape) even though it is many separate lines and dots.
- **Overload control:** *filtering* (regions, min connections), *level of detail* (hub routes only by default, all routes on selection), *aggregation* (region route matrix, hub ranking), and *one* side panel that shows either the hub list or the airport details.

## Project structure

```text
airport_flight_network/
├── data/                      airports.dat, routes.dat
├── templates/dashboard.html   dashboard UI (HTML/CSS/JS template)
├── lib/leaflet/               Leaflet map library (bundled, works offline except map tiles)
├── output/                    created by analyze_graph.py
├── download_data.py
├── check_data.py
├── clean_data.py
├── build_graph.py
├── analyze_graph.py
├── visualize_network.py       builds the graph + writes airport_map.html
├── airport_map.html           generated dashboard
├── old_versions/              earlier folium-based scripts (kept for reference)
└── README.md
```

## Requirements

- Python 3.10 or newer.
- `visualize_network.py` uses only the standard library.
- `analyze_graph.py`, `build_graph.py` and `clean_data.py` need `pandas` and `networkx`:

```powershell
python -m pip install pandas networkx
```

- Internet access in the browser is needed for the map background tiles (Esri / OpenStreetMap).

## Dataset and citation

- **Source:** OpenFlights airport and route databases, https://openflights.org/data (files used: `data/airports.dat` and `data/routes.dat`).
- **Licence:** Open Database License (ODbL). Users must acknowledge the source and license any publicly shared derived works under a free licence.
- **Suggested citation:** OpenFlights. "Airport, airline and route data." https://openflights.org/data (accessed October 2026).
- **Snapshot caveat:** the OpenFlights page states that its route-data provider stopped updating in June 2014 (67,663 routes, 3,321 airports, 548 airlines as of June 2014) and calls the route data "of historical value only." This network therefore reflects 2014 airline schedules, not current ones.
- **Preprocessing:** `check_data.py`, `clean_data.py`, `build_graph.py` and `analyze_graph.py` inspect, clean and measure the data; `visualize_network.py` repeats the same cleaning so counts agree.

## How to run

Run commands from the root `airport_flight_network` folder.

### 1. Check the input data

```powershell
python check_data.py
```

### 2. Clean and inspect the data

```powershell
python clean_data.py
```

This script cleans the data in memory and prints counts and samples. It does not currently write cleaned CSV files.

### 3. Build and inspect the directed graph

```powershell
python build_graph.py
```

This script creates a NetworkX `DiGraph`, adds airports as nodes and valid routes as directed edges, and prints graph counts and samples. It does not currently save the graph object to disk.

### 4. Run graph analysis

```powershell
python analyze_graph.py
```

This script prints graph-level statistics and top-airport rankings, and creates an `output` folder containing:

- `airport_graph_analysis.csv`
- `top_10_airports.csv`
- `isolated_airports.csv`
- `graph_summary.txt`

Note that the graph is a directed simple graph: repeated records for the same ordered source/destination pair are represented as one edge, not separate airline-specific edges.

### 5. Generate the interactive map

```powershell
python visualize_network.py
```

The script reads the data, builds the graph, and generates `airport_map.html` in the project root from `templates/dashboard.html`. Re-run it after editing the template.

### 6. Open the map in a browser

Open a second terminal in the same project folder and run:

```powershell
python -m http.server 8000
```

Keep that terminal open while using the map. In a browser, visit:

```text
http://localhost:8000/airport_map.html
```

If the page does not load, confirm the server is running and that `airport_map.html` exists in the folder being served. After regenerating the HTML, refresh the browser with `Ctrl + F5`.

## Graph model and measures

- **Vertex (node):** an airport identified by its IATA code in the graph.
- **Directed edge:** a route from a source airport to a destination airport.
- **In-degree:** number of distinct incoming neighbors in the directed graph.
- **Out-degree:** number of distinct outgoing neighbors.
- **Total degree:** in-degree plus out-degree for the directed graph.
- **Density:** proportion of possible directed edges that are present.
- **Weakly connected components:** groups connected when edge directions are ignored.
- **Strongly connected components:** groups in which each vertex can reach every other vertex by directed paths.
- **Isolated airport:** a node with degree zero in the cleaned graph.

The graph measures describe the cleaned dataset and its graph representation. An airport classified as isolated in this graph is not necessarily an airport with no real-world flights; it may have no valid route records after preprocessing.

## Current limitations and interpretation notes

- The overview is a selected view (hub-to-hub routes); individual routes are shown on demand. Only airports with at least one route are plotted (3,257 of 6,072 airports with IATA codes).
- `DiGraph` collapses duplicate edges with the same ordered source/destination pair; it does not represent the number of flights or airlines on that pair.
- Dataset counts can differ between scripts if their cleaning or filtering steps differ.
- Geographic and route records can be incomplete or outdated. Interpret statistics as properties of the dataset, not a definitive description of current airline operations.
- The exact dataset source and attribution should be verified and included before submission.

