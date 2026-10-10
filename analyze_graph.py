
import os
import pandas as pd
import networkx as nx

# ==========================================
# 1. SETUP
# ==========================================

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# 2. LOAD AIRPORT DATA
# ==========================================

airports = pd.read_csv("data/airports.dat", header=None)

airports.columns = [
    "airport_id", "name", "city", "country",
    "iata", "icao", "latitude", "longitude",
    "altitude", "timezone", "dst", "tz_database",
    "type", "source"
]

# Keep airports with valid IATA codes and coordinates
airports = airports[
    airports["iata"].notna()
    & (airports["iata"] != "\\N")
].copy()

airports["iata"] = airports["iata"].astype(str).str.strip()

airports["latitude"] = pd.to_numeric(
    airports["latitude"], errors="coerce"
)
airports["longitude"] = pd.to_numeric(
    airports["longitude"], errors="coerce"
)

airports = airports.dropna(
    subset=["latitude", "longitude"]
)

airports = airports[
    airports["latitude"].between(-90, 90)
    & airports["longitude"].between(-180, 180)
]

# One node per IATA code
airports = airports.drop_duplicates(
    subset=["iata"], keep="first"
)

# ==========================================
# 3. LOAD AND CLEAN ROUTES
# ==========================================

routes = pd.read_csv("data/routes.dat", header=None)

routes.columns = [
    "airline", "airline_id", "source_airport",
    "source_airport_id", "destination_airport",
    "destination_airport_id", "codeshare",
    "stops", "equipment"
]

routes = routes.replace("\\N", pd.NA)

routes = routes.dropna(
    subset=["source_airport", "destination_airport"]
).copy()

routes["source_airport"] = (
    routes["source_airport"].astype(str).str.strip()
)
routes["destination_airport"] = (
    routes["destination_airport"].astype(str).str.strip()
)

valid_airports = set(airports["iata"])

routes = routes[
    routes["source_airport"].isin(valid_airports)
    & routes["destination_airport"].isin(valid_airports)
].copy()

# ==========================================
# 4. BUILD DIRECTED GRAPH
# ==========================================

G = nx.DiGraph()

for _, airport in airports.iterrows():
    G.add_node(
        airport["iata"],
        name=airport["name"],
        city=airport["city"],
        country=airport["country"],
        latitude=airport["latitude"],
        longitude=airport["longitude"]
    )

for _, route in routes.iterrows():
    G.add_edge(
        route["source_airport"],
        route["destination_airport"]
    )

# Note: DiGraph stores one edge per ordered airport pair.
# Duplicate routes for the same pair are not counted multiple times.

# ==========================================
# 5. NODE-LEVEL ANALYSIS
# ==========================================

in_degree = dict(G.in_degree())
out_degree = dict(G.out_degree())
total_degree = dict(G.degree())

weak_components = list(nx.weakly_connected_components(G))
strong_components = list(nx.strongly_connected_components(G))

component_size = {}

for component_id, component in enumerate(
    sorted(weak_components, key=len, reverse=True), start=1
):
    for node in component:
        component_size[node] = len(component)

analysis = pd.DataFrame({
    "IATA": list(G.nodes()),
    "In_Degree": [in_degree[n] for n in G.nodes()],
    "Out_Degree": [out_degree[n] for n in G.nodes()],
    "Total_Degree": [total_degree[n] for n in G.nodes()],
    "Weak_Component_Size": [
        component_size[n] for n in G.nodes()
    ]
})

airport_info = airports[
    ["iata", "name", "city", "country"]
].copy()

airport_info.columns = ["IATA", "Airport", "City", "Country"]

analysis = analysis.merge(
    airport_info, on="IATA", how="left"
)

analysis = analysis[
    [
        "IATA", "Airport", "City", "Country",
        "In_Degree", "Out_Degree", "Total_Degree",
        "Weak_Component_Size"
    ]
]

# ==========================================
# 6. GRAPH-LEVEL STATISTICS
# ==========================================

number_of_nodes = G.number_of_nodes()
number_of_edges = G.number_of_edges()

density = nx.density(G) if number_of_nodes > 1 else 0.0

isolated_airports = [
    node for node in G.nodes()
    if G.degree(node) == 0
]

# Pendant vertex = an airport linked to exactly ONE other airport
# (counting neighbours in either direction).
pendant_airports = [
    node for node in G.nodes()
    if len(set(G.successors(node)) | set(G.predecessors(node))
           ) == 1
]

largest_weak_component = (
    max(weak_components, key=len) if weak_components else set()
)

largest_strong_component = (
    max(strong_components, key=len) if strong_components else set()
)

summary = {
    "Number of airport vertices": number_of_nodes,
    "Number of unique directed route edges": number_of_edges,
    "Directed graph density": density,
    "Number of weakly connected components": len(weak_components),
    "Largest weak component size": len(largest_weak_component),
    "Number of strongly connected components": len(strong_components),
    "Largest strong component size": len(largest_strong_component),
    "Number of isolated airports": len(isolated_airports),
    "Number of pendant airports (1 neighbour)": len(pendant_airports),
    "Average in-degree": (
        sum(in_degree.values()) / number_of_nodes
        if number_of_nodes else 0
    ),
    "Average out-degree": (
        sum(out_degree.values()) / number_of_nodes
        if number_of_nodes else 0
    ),
    "Maximum in-degree": max(in_degree.values(), default=0),
    "Maximum out-degree": max(out_degree.values(), default=0),
}

# ==========================================
# 7. DISPLAY GRAPH STATISTICS
# ==========================================

print("\n========== GRAPH SUMMARY ==========\n")

for key, value in summary.items():
    if isinstance(value, float):
        print(f"{key}: {value:.6f}")
    else:
        print(f"{key}: {value}")

# ==========================================
# 8. TOP 10 AIRPORTS
# ==========================================

print("\n========== TOP 10 MOST CONNECTED AIRPORTS ==========\n")

top_airports = analysis.sort_values(
    ["Total_Degree", "IATA"],
    ascending=[False, True]
).head(10)

print(
    top_airports[
        [
            "IATA", "Airport", "City", "Country",
            "In_Degree", "Out_Degree", "Total_Degree"
        ]
    ].to_string(index=False)
)

print("\n========== TOP 10 BY IN-DEGREE ==========\n")

print(
    analysis.sort_values(
        ["In_Degree", "IATA"],
        ascending=[False, True]
    ).head(10)[
        ["IATA", "Airport", "Country", "In_Degree"]
    ].to_string(index=False)
)

print("\n========== TOP 10 BY OUT-DEGREE ==========\n")

print(
    analysis.sort_values(
        ["Out_Degree", "IATA"],
        ascending=[False, True]
    ).head(10)[
        ["IATA", "Airport", "Country", "Out_Degree"]
    ].to_string(index=False)
)

# ==========================================
# 9. ISOLATED AIRPORTS
# ==========================================

isolated_df = analysis[
    analysis["Total_Degree"] == 0
].copy()

print(
    f"\nNumber of isolated airports: {len(isolated_df)}"
)

# ==========================================
# 10. EXPORT RESULTS
# ==========================================

analysis.to_csv(
    os.path.join(OUTPUT_DIR, "airport_graph_analysis.csv"),
    index=False
)

top_airports.to_csv(
    os.path.join(OUTPUT_DIR, "top_10_airports.csv"),
    index=False
)

isolated_df.to_csv(
    os.path.join(OUTPUT_DIR, "isolated_airports.csv"),
    index=False
)

with open(
    os.path.join(OUTPUT_DIR, "graph_summary.txt"),
    "w",
    encoding="utf-8"
) as file:
    file.write("GLOBAL AIRPORT NETWORK - GRAPH SUMMARY\n")
    file.write("=" * 45 + "\n\n")

    for key, value in summary.items():
        if isinstance(value, float):
            file.write(f"{key}: {value:.6f}\n")
        else:
            file.write(f"{key}: {value}\n")

print("\n========== FILES SAVED ==========")
print("output/airport_graph_analysis.csv")
print("output/top_10_airports.csv")
print("output/isolated_airports.csv")
print("output/graph_summary.txt")
print("\nGraph analysis completed successfully.")
