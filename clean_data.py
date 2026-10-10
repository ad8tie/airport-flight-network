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
# 3. CLEAN AIRPORT DATA
# ==========================================

# Remove airports without IATA codes
airports = airports[
    airports["iata"].notna() &
    (airports["iata"] != "\\N")
]

# Convert coordinates to numbers
airports["latitude"] = pd.to_numeric(
    airports["latitude"],
    errors="coerce"
)

airports["longitude"] = pd.to_numeric(
    airports["longitude"],
    errors="coerce"
)

# Remove airports without valid coordinates
airports = airports.dropna(
    subset=["latitude", "longitude"]
)


# ==========================================
# 4. CLEAN ROUTE DATA
# ==========================================

# Replace missing values
routes = routes.replace("\\N", pd.NA)

# Remove routes without source/destination
routes = routes.dropna(
    subset=[
        "source_airport",
        "destination_airport"
    ]
)


# ==========================================
# 5. KEEP ONLY ROUTES WITH VALID AIRPORTS
# ==========================================

valid_airports = set(airports["iata"])

routes = routes[
    routes["source_airport"].isin(valid_airports) &
    routes["destination_airport"].isin(valid_airports)
]


# ==========================================
# 6. DISPLAY CLEANING RESULTS
# ==========================================

print("========== CLEANING COMPLETE ==========")

print("Valid airports:", len(airports))
print("Valid routes:", len(routes))

print("\nSample cleaned airports:")
print(
    airports[
        ["iata", "name", "city", "country",
         "latitude", "longitude"]
    ].head()
)

print("\nSample cleaned routes:")
print(
    routes[
        ["source_airport", "destination_airport"]
    ].head()
)