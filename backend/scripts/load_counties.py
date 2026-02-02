import os
from pathlib import Path

import geopandas as gpd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

GEOJSON_PATH = os.getenv("COUNTIES_GEOJSON", "data/census/us_counties_2023_5m.geojson")
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DB_URL)

def main():
    gdf = gpd.read_file(GEOJSON_PATH).to_crs(epsg=4326)

    # Census files include these columns:
    gdf = gdf.rename(columns={"GEOID": "geoid", "NAME": "name", "STATEFP": "state_fips"})

    # Keep only what our schema expects + geometry
    gdf = gdf[["geoid", "name", "state_fips", "geometry"]]
    gdf = gdf.rename(columns={"geometry": "geom"})
    gdf = gdf.set_geometry("geom")

    gdf.to_postgis("counties", engine, if_exists="append", index=False)
    print(f"Loaded {len(gdf)} counties into Neon.")

if __name__ == "__main__":
    main()
