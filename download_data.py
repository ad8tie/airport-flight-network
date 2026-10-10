import urllib.request
import os

os.makedirs("data", exist_ok=True)

airport_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
route_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"

urllib.request.urlretrieve(
    airport_url,
    "data/airports.dat"
)

urllib.request.urlretrieve(
    route_url,
    "data/routes.dat"
)

print("Datasets downloaded successfully!")