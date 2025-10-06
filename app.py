from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import shutil
from converter import kmz_to_shapefile

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("file")
        if not files:
            return render_template("index.html", message="⚠️ Please upload at least one KMZ file.")

        # Clear old files
        if os.path.exists(OUTPUT_FOLDER):
            shutil.rmtree(OUTPUT_FOLDER)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        kmz_paths = []
        for file in files:
            if file.filename.endswith(".kmz"):
                save_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(save_path)
                kmz_paths.append(save_path)

        try:
            results = kmz_to_shapefile(kmz_paths, OUTPUT_FOLDER)
            # Convert all to GeoJSON preview (first one)
            geojson_file = os.path.basename(results[0][1]) if results else None
            return redirect(url_for("map_preview", geojson_file=geojson_file))
        except Exception as e:
            return render_template("index.html", message=f"❌ Error: {e}")

    return render_template("index.html", message=None)

@app.route("/map/<geojson_file>")
def map_preview(geojson_file):
    return render_template("map.html", geojson_file=geojson_file)

@app.route("/download")
def download():
    shutil.make_archive("output/all_converted_files", "zip", OUTPUT_FOLDER)
    return send_file("output/all_converted_files.zip", as_attachment=True)

@app.route("/geojson/<geojson_file>")
def serve_geojson(geojson_file):
    return send_file(os.path.join(OUTPUT_FOLDER, geojson_file))

if __name__ == "__main__":
    app.run(debug=True)
