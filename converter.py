import zipfile
import geopandas as gpd
import os
import shutil
import fiona

def convert_single_kmz(kmz_path, output_dir):
    """Convert a single KMZ file into a Shapefile + GeoJSON"""
    base_name = os.path.splitext(os.path.basename(kmz_path))[0]
    temp_extract_dir = os.path.join(output_dir, f"temp_{base_name}")

    if os.path.exists(temp_extract_dir):
        shutil.rmtree(temp_extract_dir)
    os.makedirs(temp_extract_dir)

    # Extract KMZ
    with zipfile.ZipFile(kmz_path, 'r') as z:
        z.extractall(temp_extract_dir)

    # Find KML
    kml_file = None
    for root, _, files in os.walk(temp_extract_dir):
        for file in files:
            if file.endswith(".kml"):
                kml_file = os.path.join(root, file)
                break
    if not kml_file:
        raise FileNotFoundError(f"No .kml file found inside {base_name}.kmz")

    # Read and export
    fiona.supported_drivers["KML"] = "rw"
    gdf = gpd.read_file(kml_file, driver="KML")

    # Shapefile + GeoJSON outputs with original filename
    shp_name = f"{base_name}.shp"
    geojson_name = f"{base_name}.geojson"

    shp_path = os.path.join(output_dir, shp_name)
    geojson_path = os.path.join(output_dir, geojson_name)

    gdf.to_file(shp_path)
    gdf.to_file(geojson_path, driver="GeoJSON")

    shutil.rmtree(temp_extract_dir)
    return shp_path, geojson_path


def kmz_to_shapefile(kmz_files, output_dir):
    """Convert multiple KMZ files"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    results = []
    for kmz_path in kmz_files:
        shp_path, geojson_path = convert_single_kmz(kmz_path, output_dir)
        results.append((shp_path, geojson_path))
    return results
