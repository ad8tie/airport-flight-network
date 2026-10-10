import pandas as pd

# ==========================================
# 1. LOAD AIRPORT DATA
# ==========================================

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


# ==========================================
# 2. LOAD ROUTE DATA
# ==========================================

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


# ==========================================
# 3. DISPLAY INFORMATION
# ==========================================

print("========== AIRPORT DATA ==========")

print(airports.head())

print("\nAirport columns:")
print(airports.columns.tolist())

print("\nNumber of airports:", len(airports))


print("\n========== ROUTE DATA ==========")

print(routes.head())

print("\nRoute columns:")
print(routes.columns.tolist())

print("\nNumber of routes:", len(routes))