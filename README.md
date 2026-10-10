<div align="center">

# 🌍 Global Airport & Flight Route Network Explorer

**Explore the connections that link the world's airports.**

An interactive graph-visualization project built to explore airport connectivity, identify major hubs, and understand the structure of a global route network.

[✨ Features](#-features) · [🧭 How It Works](#-how-it-works) · [🚀 Run Locally](#-run-locally) · [📊 Graph Model--visual-encoding](#-graph-model--visual-encoding)

</div>

---

## ✨ Features

| Feature | What you can explore |
|---|---|
| 🗺️ **Interactive world map** | Explore airports at their geographic coordinates and zoom or pan around the network. |
| 🔎 **Airport search** | Find airports by IATA code, name, city, or country. |
| 🎛️ **Dynamic filters** | Filter by region or minimum connections, toggle routes, and change map style. |
| 📍 **Airport details** | Select an airport to inspect incoming/outgoing connections, rank, and busiest links. |
| 🔗 **Linked interactions** | Explore the relationship between the hub ranking and map selection. |
| 📈 **Network analysis** | Calculate degree measures, density, connected components, isolated airports, and regional route patterns. |

## 🧭 How It Works

```text
        OpenFlights dataset
                 │
                 ▼
      Clean airports and routes
                 │
                 ▼
      Build a directed graph
                 │
                 ▼
       Calculate graph metrics
                 │
                 ▼
  Interactive map + hub ranking
   filters + airport-level details
```

### 🎨 Visual Encoding

- **Position** → airport latitude and longitude
- **Colour** → airport region
- **Marker size** → number of connected airports
- **Lines** → directed airport-to-airport routes
- **Highlight colour** → selected airport and its routes

Filtering and showing detailed routes on selection help keep the overview readable.

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-Graph_Analysis-444444?style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458?style=flat-square&logo=pandas&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Interactive_UI-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Leaflet](https://img.shields.io/badge/Leaflet-Interactive_Maps-199900?style=flat-square&logo=leaflet&logoColor=white)
![HTML/CSS](https://img.shields.io/badge/HTML%2FCSS-Dashboard-E34F26?style=flat-square&logo=html5&logoColor=white)

## 🚀 Run Locally

### 1. Prerequisites

- Python 3.10+
- `data/airports.dat` and `data/routes.dat`
- Internet access for map background tiles

### 2. Install dependencies

Run these commands from the project root:

```powershell
python -m pip install pandas networkx
```

### 3. Check, build, and analyse the data

```powershell
python check_data.py
python clean_data.py
python build_graph.py
python analyze_graph.py
```

### 4. Generate and launch the dashboard

```powershell
python visualize_network.py
python -m http.server 8000
```

Open **http://localhost:8000/airport_map.html** in your browser. Keep the terminal running while using the app.

> After changing `templates/dashboard.html`, run `python visualize_network.py` again and refresh the page.

## 📊 Graph Model & Visual Encoding

- **Vertices (nodes):** airports identified by IATA code.
- **Directed edges:** route records from a source airport to a destination airport.
- **In-degree / out-degree:** distinct incoming and outgoing neighbours.
- **Density:** proportion of possible directed edges present.
- **Connected components:** groups of airports connected through routes.
- **Isolated airports:** airports with no valid route edges after preprocessing.

## 📁 Project Structure

```text
.
├── data/                    # Airport and route source files
├── templates/
│   └── dashboard.html       # Dashboard HTML/CSS/JavaScript
├── lib/leaflet/             # Leaflet assets
├── output/                  # Generated graph-analysis reports
├── check_data.py            # Input-data checks
├── clean_data.py            # Data cleaning and inspection
├── build_graph.py           # Directed graph construction
├── analyze_graph.py         # Network metrics and CSV/text reports
├── visualize_network.py     # Generates the interactive dashboard
├── airport_map.html         # Generated dashboard
└── README.md
```

## 🗃️ Dataset & Limitations

**Dataset:** [OpenFlights airport and route database](https://openflights.org/data)

The route data is historical (last updated in 2014), so this project is intended for **network exploration, not live flight tracking**. Each unique source–destination pair is treated as one directed edge; the graph does not represent flight frequency or airline-specific duplicates.

OpenFlights data is distributed under the Open Database License (ODbL). Review its attribution and share-alike requirements before redistributing derived data.

---

<div align="center">

**Built to turn raw route records into an explorable network.**

</div>
