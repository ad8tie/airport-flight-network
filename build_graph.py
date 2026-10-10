import pandas as pd
import networkx as nx

# Load airports
airports = pd.read_csv(
    "data/airports.dat",
    header=None
)

airports.columns = [
    "airport_id",
    "name",
    "city",
    "country",
    "iata",
    "icao",
    "latitude",
    "longitude",
    "altitude",
    "timezone",
    "dst",
    "tz_database",
    "type",
    "source"
]

# Load routes
routes = pd.read_csv(
    "data/routes.dat",
    header=None
)

routes.columns = [
    "airline",
    "airline_id",
    "source_airport",
    "source_airport_id",
    "destination_airport",
    "destination_airport_id",
    "codeshare",
    "stops",
    "equipment"
]

# Clean airports
airports = airports[
    airports["iata"].notna() &
    (airports["iata"] != "\\N")
]

airports["latitude"] = pd.to_numeric(
    airports["latitude"],
    errors="coerce"
)

airports["longitude"] = pd.to_numeric(
    airports["longitude"],
    errors="coerce"
)

airports = airports.dropna(
    subset=["latitude", "longitude"]
)

# Clean routes
routes = routes.replace("\\N", pd.NA)

routes = routes.dropna(
    subset=["source_airport", "destination_airport"]
)

# Keep routes connecting valid airports
valid_airports = set(airports["iata"])

routes = routes[
    routes["source_airport"].isin(valid_airports) &
    routes["destination_airport"].isin(valid_airports)
]

# Create directed graph
G = nx.DiGraph()

# Add airports as nodes
for _, airport in airports.iterrows():

    G.add_node(
        airport["iata"],
        name=airport["name"],
        city=airport["city"],
        country=airport["country"],
        latitude=airport["latitude"],
        longitude=airport["longitude"]
    )

# Add routes as edges
for _, route in routes.iterrows():

    G.add_edge(
        route["source_airport"],
        route["destination_airport"]
    )

# Display results
print("========== GRAPH CREATED ==========")

print("Number of airports:", G.number_of_nodes())

print("Number of routes:", G.number_of_edges())

print("\nFirst 10 airports:")
print(list(G.nodes())[:10])

print("\nFirst 10 routes:")
print(list(G.edges())[:10])